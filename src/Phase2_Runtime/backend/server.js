const express = require('express');
const cors = require('cors');
const { Pool } = require('pg');
const multer = require('multer');
const fs = require('fs');
const OpenAI = require('openai');

require('dotenv').config();

const app = express();

app.use(cors());
app.use(express.json());

const upload = multer({
  dest: 'uploads/',
});

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: {
    rejectUnauthorized: false,
  },
});

app.get('/', (req, res) => {
  res.send('Backend is working ✔');
});

// =========================
// REGISTER
// =========================

app.post('/users', async (req, res) => {
  try {
    let { name, email, password } = req.body;

    name = name?.trim();
    email = email?.trim();
    password = password?.trim();

    if (!name || !email || !password) {
      return res.status(400).json({ message: 'All fields are required' });
    }

    if (!email.includes('@')) {
      return res.status(400).json({ message: 'Invalid email format' });
    }

    if (password.length < 6) {
      return res.status(400).json({
        message: 'Password must be at least 6 characters',
      });
    }

    const checkUser = await pool.query(
      'SELECT * FROM users WHERE email = $1',
      [email]
    );

    if (checkUser.rows.length > 0) {
      return res.status(409).json({ message: 'Email already exists' });
    }

    const result = await pool.query(
      `
      INSERT INTO users (name, email, password)
      VALUES ($1, $2, $3)
      RETURNING userid, name, email
      `,
      [name, email, password]
    );

    res.status(201).json({
      message: 'User created successfully',
      user: result.rows[0],
    });

  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Server Error' });
  }
});

// =========================
// LOGIN
// =========================

app.post('/login', async (req, res) => {
  try {
    let { email, password } = req.body;

    email = email?.trim();
    password = password?.trim();

    if (!email || !password) {
      return res.status(400).json({
        message: 'Email and password are required',
      });
    }

    const result = await pool.query(
      `
      SELECT userid, name, email
      FROM users
      WHERE email = $1 AND password = $2
      `,
      [email, password]
    );

    if (result.rows.length === 0) {
      return res.status(401).json({
        message: 'Invalid email or password',
      });
    }

    res.status(200).json({
      message: 'Login successful',
      user: result.rows[0],
    });

  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Server Error' });
  }
});

// =========================
// GET USERS
// =========================

app.get('/users', async (req, res) => {
  try {
    const result = await pool.query(
      'SELECT userid, name, email FROM users'
    );

    res.status(200).json(result.rows);

  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Server Error' });
  }
});

// =========================
// GET USER BY ID
// =========================

app.get('/users/:id', async (req, res) => {
  try {
    const { id } = req.params;

    const result = await pool.query(
      `
      SELECT userid, name, email
      FROM users
      WHERE userid = $1
      `,
      [id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({
        message: 'User not found',
      });
    }

    res.status(200).json(result.rows[0]);

  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Server Error' });
  }
});

// =========================
// SCAN PRINTER
// =========================

app.post('/scan-printer', upload.single('image'), async (req, res) => {
  let imagePath = null;

  try {
    if (!req.file) {
      return res.status(400).json({
        success: false,
        message: 'Image file is required',
      });
    }

    imagePath = req.file.path;

    const imageBase64 = fs.readFileSync(imagePath, {
      encoding: 'base64',
    });

    const vlmResponse = await client.responses.create({
      model: 'gpt-4.1-mini',
      input: [
        {
          role: 'user',
          content: [
            {
              type: 'input_text',
              text:
                'Identify the printer model from this image. Return ONLY the printer model name. If unclear return UNKNOWN.',
            },
            {
              type: 'input_image',
              image_url: `data:image/jpeg;base64,${imageBase64}`,
            },
          ],
        },
      ],
    });

    const printerModel = vlmResponse.output_text.trim();

    if (printerModel.toUpperCase() === 'UNKNOWN') {
      return res.status(200).json({
        success: false,
        source: 'vlm',
        printer_model: printerModel,
        message: 'Printer model could not be identified.',
      });
    }

    const deviceResult = await pool.query(
      `
      SELECT *
      FROM devices
      WHERE devicename ILIKE $1
      LIMIT 1
      `,
      [`%${printerModel}%`]
    );

    if (deviceResult.rows.length > 0) {
      return res.status(200).json({
        success: true,
        source: 'database',
        printer_model: printerModel,
        device: deviceResult.rows[0],
      });
    }

    const llmResponse = await client.responses.create({
      model: 'gpt-4.1-mini',
      input: `
Generate a printer setup and troubleshooting guide
for this printer model:

${printerModel}

Return JSON only using this structure:

{
  "device_name": "${printerModel}",
  "device_type": "Printer",
  "guide_title": "${printerModel} Setup and Troubleshooting Guide",
  "steps": [
    "",
    "",
    ""
  ]
}
`,
    });

    let generatedGuideText = llmResponse.output_text;

    generatedGuideText = generatedGuideText
      .replace('```json', '')
      .replace('```', '')
      .trim();

    const parsedGuide = JSON.parse(generatedGuideText);

    const existingDevice = await pool.query(
      `
      SELECT deviceid
      FROM devices
      WHERE devicename ILIKE $1
      LIMIT 1
      `,
      [parsedGuide.device_name]
    );

    let deviceId;

    if (existingDevice.rows.length > 0) {
      deviceId = existingDevice.rows[0].deviceid;
    } else {
      const insertDevice = await pool.query(
        `
        INSERT INTO devices (devicename, devicetype)
        VALUES ($1, $2)
        RETURNING deviceid
        `,
        [
          parsedGuide.device_name,
          parsedGuide.device_type,
        ]
      );

      deviceId = insertDevice.rows[0].deviceid;
    }

    const insertGuide = await pool.query(
      `
      INSERT INTO guides (deviceid, title, datecreated)
      VALUES ($1, $2, CURRENT_DATE)
      RETURNING guideid
      `,
      [
        deviceId,
        parsedGuide.guide_title,
      ]
    );

    const guideId = insertGuide.rows[0].guideid;

    for (let i = 0; i < parsedGuide.steps.length; i++) {
      await pool.query(
        `
        INSERT INTO steps (guideid, stepnumber, description)
        VALUES ($1, $2, $3)
        `,
        [
          guideId,
          i + 1,
          parsedGuide.steps[i],
        ]
      );
    }

    return res.status(200).json({
      success: true,
      source: 'llm_saved_to_database',
      printer_model: printerModel,
      device_id: deviceId,
      guide_id: guideId,
      guide: parsedGuide,
    });

  } catch (error) {
    console.error(error);

    return res.status(500).json({
      success: false,
      error: error.message,
    });

  } finally {
    if (imagePath && fs.existsSync(imagePath)) {
      fs.unlinkSync(imagePath);
    }
  }
});

// =========================
// GET DEVICE GUIDE
// =========================

app.get('/devices/:id/guide', async (req, res) => {
  try {
    const { id } = req.params;

    const deviceResult = await pool.query(
      `
      SELECT deviceid, devicename, devicetype
      FROM devices
      WHERE deviceid = $1
      `,
      [id]
    );

    if (deviceResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Device not found',
      });
    }

    const guideResult = await pool.query(
      `
      SELECT guideid, title, datecreated, createdat
      FROM guides
      WHERE deviceid = $1
      ORDER BY createdat DESC
      LIMIT 1
      `,
      [id]
    );

    if (guideResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Guide not found for this device',
      });
    }

    const guide = guideResult.rows[0];

    const stepsResult = await pool.query(
      `
      SELECT stepid, stepnumber, description
      FROM steps
      WHERE guideid = $1
      ORDER BY stepnumber ASC
      `,
      [guide.guideid]
    );

    res.status(200).json({
      success: true,
      device: deviceResult.rows[0],
      guide: guide,
      steps: stepsResult.rows,
    });

  } catch (error) {
    console.error(error);

    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

// =========================
// USER OPEN DEVICE
// يسجل أن المستخدم فتح طابعة معينة
// =========================

app.post('/user-progress/open-device', async (req, res) => {
  try {
    const { userId, deviceId } = req.body;

    if (!userId || !deviceId) {
      return res.status(400).json({
        success: false,
        message: 'userId and deviceId are required',
      });
    }

    const existing = await pool.query(
      `
      SELECT progressid
      FROM userprogress
      WHERE userid = $1 AND deviceid = $2
      LIMIT 1
      `,
      [userId, deviceId]
    );

    if (existing.rows.length > 0) {
      const updated = await pool.query(
        `
        UPDATE userprogress
        SET updatedat = CURRENT_TIMESTAMP,
            status = 'opened'
        WHERE userid = $1 AND deviceid = $2
        RETURNING *
        `,
        [userId, deviceId]
      );

      return res.status(200).json({
        success: true,
        message: 'Device activity updated',
        progress: updated.rows[0],
      });
    }

    const inserted = await pool.query(
      `
      INSERT INTO userprogress
      (userid, deviceid, progresspercent, status, updatedat)
      VALUES ($1, $2, 0, 'opened', CURRENT_TIMESTAMP)
      RETURNING *
      `,
      [userId, deviceId]
    );

    return res.status(201).json({
      success: true,
      message: 'Device activity created',
      progress: inserted.rows[0],
    });

  } catch (error) {
    console.error(error);

    return res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

// =========================
// GET USER RECENT DEVICES
// يجيب آخر الطابعات التي فتحها المستخدم
// =========================

app.get('/users/:userId/recent-devices', async (req, res) => {
  try {
    const { userId } = req.params;

    const result = await pool.query(
      `
      SELECT
        d.deviceid,
        d.devicename,
        d.devicetype,
        g.guideid,
        g.title AS guide_title,
        up.progresspercent,
        up.status,
        up.updatedat AS last_opened
      FROM userprogress up
      JOIN devices d
        ON up.deviceid = d.deviceid
      LEFT JOIN guides g
        ON d.deviceid = g.deviceid
      WHERE up.userid = $1
      ORDER BY up.updatedat DESC
      LIMIT 10
      `,
      [userId]
    );

    return res.status(200).json({
      success: true,
      devices: result.rows,
    });

  } catch (error) {
    console.error(error);

    return res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

// =========================
// UPDATE USER PROGRESS
// =========================

app.post('/user-progress/update', async (req, res) => {
  try {
    const { userId, deviceId, progressPercent, status } = req.body;

    if (!userId || !deviceId || progressPercent === undefined) {
      return res.status(400).json({
        success: false,
        message: 'userId, deviceId, and progressPercent are required',
      });
    }

    const existing = await pool.query(
      `
      SELECT progressid
      FROM userprogress
      WHERE userid = $1 AND deviceid = $2
      LIMIT 1
      `,
      [userId, deviceId]
    );

    if (existing.rows.length > 0) {
      const updated = await pool.query(
        `
        UPDATE userprogress
        SET progresspercent = $1,
            status = $2,
            updatedat = CURRENT_TIMESTAMP
        WHERE userid = $3 AND deviceid = $4
        RETURNING *
        `,
        [
          progressPercent,
          status ?? 'in_progress',
          userId,
          deviceId,
        ]
      );

      return res.status(200).json({
        success: true,
        progress: updated.rows[0],
      });
    }

    const inserted = await pool.query(
      `
      INSERT INTO userprogress
      (userid, deviceid, progresspercent, status, updatedat)
      VALUES ($1, $2, $3, $4, CURRENT_TIMESTAMP)
      RETURNING *
      `,
      [
        userId,
        deviceId,
        progressPercent,
        status ?? 'in_progress',
      ]
    );

    return res.status(201).json({
      success: true,
      progress: inserted.rows[0],
    });

  } catch (error) {
    console.error(error);

    return res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

// =========================
// GENERAL RECENT DEVICES
// للاختبار فقط: يجيب آخر أجهزة موجودة بالداتابيس
// =========================

app.get('/recent-devices', async (req, res) => {
  try {
    const result = await pool.query(
      `
      SELECT
        d.deviceid,
        d.devicename,
        d.devicetype,
        g.title AS guide_title,
        g.createdat AS last_opened
      FROM devices d
      LEFT JOIN guides g
        ON d.deviceid = g.deviceid
      ORDER BY g.createdat DESC NULLS LAST
      LIMIT 10
      `
    );

    res.status(200).json({
      success: true,
      devices: result.rows,
    });

  } catch (error) {
    console.error(error);

    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

app.post('/feedback', async (req, res) => {
  try {
    const { userId, guideId, rating, comment } = req.body;

    if (!userId || !guideId || !rating) {
      return res.status(400).json({
        success: false,
        message: 'userId, guideId, and rating are required',
      });
    }

    const result = await pool.query(
      `
      INSERT INTO feedback (userid, guideid, rating, comment)
      VALUES ($1, $2, $3, $4)
      RETURNING *
      `,
      [userId, guideId, rating, comment ?? null]
    );

    return res.status(201).json({
      success: true,
      feedback: result.rows[0],
    });

  } catch (error) {
    console.error(error);

    return res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

// =========================
// START SERVER
// =========================

console.log('RUNNING THIS FILE:', __filename);

app.listen(3000, () => {
  console.log('Server running on http://localhost:3000 ✔');
});