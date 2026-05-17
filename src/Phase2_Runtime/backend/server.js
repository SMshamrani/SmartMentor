const express = require('express');
const cors = require('cors');
const { Pool } = require('pg');
const multer = require('multer');
const fs = require('fs');
const OpenAI = require('openai');
const bcrypt = require('bcrypt');

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
    email = email?.trim().toLowerCase();
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
      'SELECT userid FROM users WHERE email = $1',
      [email]
    );

    if (checkUser.rows.length > 0) {
      return res.status(409).json({ message: 'Email already exists' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);

    const result = await pool.query(
      `
      INSERT INTO users (name, email, password)
      VALUES ($1, $2, $3)
      RETURNING userid, name, email
      `,
      [name, email, hashedPassword]
    );

    res.status(201).json({
      message: 'User created successfully',
      user: result.rows[0],
    });
  } catch (error) {
    console.error('Register Error:', error.message);
    res.status(500).json({ message: 'Server Error' });
  }
});

// =========================
// LOGIN
// =========================

app.post('/login', async (req, res) => {
  try {
    let { email, password } = req.body;

    email = email?.trim().toLowerCase();
    password = password?.trim();

    if (!email || !password) {
      return res.status(400).json({
        message: 'Email and password are required',
      });
    }

    const result = await pool.query(
      `
      SELECT userid, name, email, password
      FROM users
      WHERE email = $1
      `,
      [email]
    );

    if (result.rows.length === 0) {
      return res.status(401).json({
        message: 'Invalid email or password',
      });
    }

    const user = result.rows[0];

    const isMatch = await bcrypt.compare(password, user.password);

    if (!isMatch) {
      return res.status(401).json({
        message: 'Invalid email or password',
      });
    }

    res.status(200).json({
      message: 'Login successful',
      user: {
        userid: user.userid,
        name: user.name,
        email: user.email,
      },
    });
  } catch (error) {
    console.error('Login Error:', error.message);
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
                'Identify the device brand and model from this image. Return ONLY the device name/model. If unclear return UNKNOWN.',
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
        message: 'Device model could not be identified.',
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

    // =========================
    // NOT FOUND → ASK LLM
    // =========================

    const llmResponse = await client.responses.create({
      model: 'gpt-4.1-mini',
      input: `
Generate complete structured device data for this device model:

${printerModel}

Return JSON only.
Do not use markdown.
Do not use code blocks.

Use exactly this structure:

{
  "device_name": "${printerModel}",
  "device_type": "Device",
  "components": [
    {
      "component_name": "",
      "description": ""
    }
  ],
  "guide": {
    "title": "${printerModel} Setup and Troubleshooting Guide",
    "steps": [
      {
        "step_number": 1,
        "description": ""
      }
    ]
  }
}

Requirements:
- Include 5 to 8 realistic device components.
- Include 6 to 10 setup/troubleshooting steps.
- Steps must be beginner friendly.
- Return valid JSON only.
`,
    });

    let generatedGuideText = llmResponse.output_text.trim();

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

    const existingGuide = await pool.query(
      `
      SELECT guideid
      FROM guides
      WHERE deviceid = $1
      LIMIT 1
      `,
      [deviceId]
    );

    let guideId;

    if (existingGuide.rows.length > 0) {
      guideId = existingGuide.rows[0].guideid;
    } else {
      const insertGuide = await pool.query(
        `
        INSERT INTO guides (deviceid, title, datecreated)
        VALUES ($1, $2, CURRENT_DATE)
        RETURNING guideid
        `,
        [
          deviceId,
          parsedGuide.guide.title,
        ]
      );

      guideId = insertGuide.rows[0].guideid;

      for (const component of parsedGuide.components) {
        await pool.query(
          `
          INSERT INTO components (deviceid, componentname, description)
          VALUES ($1, $2, $3)
          `,
          [
            deviceId,
            component.component_name,
            component.description,
          ]
        );
      }

      for (const step of parsedGuide.guide.steps) {
        await pool.query(
          `
          INSERT INTO steps (guideid, stepnumber, description)
          VALUES ($1, $2, $3)
          `,
          [
            guideId,
            step.step_number,
            step.description,
          ]
        );
      }
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

    const componentsResult = await pool.query(
      `
      SELECT componentid, componentname, description
      FROM components
      WHERE deviceid = $1
      ORDER BY componentid ASC
      `,
      [id]
    );

    res.status(200).json({
      success: true,
      device: deviceResult.rows[0],
      guide: guide,
      steps: stepsResult.rows,
      components: componentsResult.rows,
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

// =========================
// FEEDBACK
// =========================

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
// SEARCH DEVICES FROM DATABASE
// =========================

app.get('/devices/search', async (req, res) => {
  try {
    const query = req.query.q?.trim();

    if (!query) {
      return res.status(400).json({
        success: false,
        message: 'Search query is required',
      });
    }

    const result = await pool.query(
      `
      SELECT
        d.deviceid,
        d.devicename,
        d.devicetype,
        g.guideid,
        g.title AS guide_title
      FROM devices d
      LEFT JOIN guides g ON d.deviceid = g.deviceid
      WHERE d.devicename ILIKE $1
         OR d.devicetype ILIKE $1
         OR g.title ILIKE $1
      ORDER BY d.createdat DESC
      LIMIT 20
      `,
      [`%${query}%`]
    );

    return res.status(200).json({
      success: true,
      devices: result.rows,
    });
  } catch (error) {
    console.error(error);
    return res.status(500).json({
      success: false,
      message: 'Server Error',
    });
  }
});

// =========================
// USER NOTIFICATIONS
// =========================

app.get('/users/:userId/notifications', async (req, res) => {
  try {
    const { userId } = req.params;

    const notifications = [];

    const completed = await pool.query(
      `
      SELECT d.devicename, up.updatedat
      FROM userprogress up
      JOIN devices d ON up.deviceid = d.deviceid
      WHERE up.userid = $1
        AND up.status = 'completed'
      ORDER BY up.updatedat DESC
      LIMIT 3
      `,
      [userId]
    );

    completed.rows.forEach((row) => {
      notifications.push({
        type: 'Device guide completed',
        title: 'Device guide completed',
        message: `You completed the guide for ${row.devicename}.`,
        date: row.updatedat,
      });
    });

    const aiGenerated = await pool.query(
  `
  SELECT d.devicename, up.updatedat
  FROM userprogress up
  JOIN devices d ON up.deviceid = d.deviceid
  WHERE up.userid = $1
    AND d.sourceid IS NULL
  ORDER BY up.updatedat DESC
  LIMIT 3
  `,
  [userId]
);

aiGenerated.rows.forEach((row) => {
  notifications.push({
    type: 'New AI guide generated',
    title: 'New AI guide generated',
    message: `A new AI guide was generated for ${row.devicename}.`,
    date: row.updatedat,
  });
});

    

    const incomplete = await pool.query(
      `
      SELECT d.devicename, up.progresspercent, up.updatedat
      FROM userprogress up
      JOIN devices d ON up.deviceid = d.deviceid
      WHERE up.userid = $1
        AND up.progresspercent > 0
        AND up.progresspercent < 100
      ORDER BY up.updatedat DESC
      LIMIT 3
      `,
      [userId]
    );

    incomplete.rows.forEach((row) => {
      notifications.push({
        type: 'Incomplete guide reminder',
        title: 'Incomplete guide reminder',
        message: `${row.devicename} is ${row.progresspercent}% completed.`,
        date: row.updatedat,
      });
    });

    const feedback = await pool.query(
      `
      SELECT f.rating, f.datesubmitted, d.devicename
      FROM feedback f
      JOIN guides g ON f.guideid = g.guideid
      JOIN devices d ON g.deviceid = d.deviceid
      WHERE f.userid = $1
      ORDER BY f.datesubmitted DESC
      LIMIT 3
      `,
      [userId]
    );

    feedback.rows.forEach((row) => {
      notifications.push({
        type: 'Feedback submitted',
        title: 'Feedback submitted',
        message: `You rated ${row.devicename} guide ${row.rating}/5.`,
        date: row.datesubmitted,
      });
    });

    const recent = await pool.query(
      `
      SELECT d.devicename, up.updatedat
      FROM userprogress up
      JOIN devices d ON up.deviceid = d.deviceid
      WHERE up.userid = $1
        AND up.status = 'opened'
      ORDER BY up.updatedat DESC
      LIMIT 3
      `,
      [userId]
    );

    recent.rows.forEach((row) => {
      notifications.push({
        type: 'Recently scanned device',
        title: 'Recently scanned device',
        message: `${row.devicename} was recently opened or scanned.`,
        date: row.updatedat,
      });
    });

    notifications.sort((a, b) => new Date(b.date) - new Date(a.date));

    return res.status(200).json({
      success: true,
      notifications,
    });
  } catch (error) {
    console.error(error);
    return res.status(500).json({
      success: false,
      message: 'Server Error',
    });
  }
});


// =======================================
// GENERATE DEVICE GUIDE USING AI
// =======================================

app.post('/generate-device-guide', async (req, res) => {

  try {

    const { deviceName } = req.body;

    if (!deviceName || deviceName.trim() === '') {

      return res.status(400).json({

        success: false,

        message: 'Device name is required',
      });
    }

    // ===================================
    // CHECK IF DEVICE ALREADY EXISTS
    // ===================================

    const existingDevice = await pool.query(

      `
      SELECT
        d.deviceid,
        d.devicename,
        d.devicetype,
        g.guideid,
        g.title AS guide_title
      FROM devices d
      LEFT JOIN guides g
        ON d.deviceid = g.deviceid
      WHERE LOWER(d.devicename) = LOWER($1)
      LIMIT 1
      `,
      [deviceName]
    );

    if (existingDevice.rows.length > 0) {

      return res.status(200).json({

        success: true,

        source: 'database',

        device: existingDevice.rows[0],
      });
    }

    // ===================================
    // GENERATE DEVICE DATA WITH AI
    // ===================================

    const prompt = `
Generate complete structured device data for this device:

${deviceName}

Return ONLY valid JSON.

Use exactly this structure:

{
  "device_name": "${deviceName}",
  "device_type": "Device",
  "components": [
    {
      "component_name": "",
      "description": ""
    }
  ],
  "guide": {
    "title": "${deviceName} Setup and Troubleshooting Guide",
    "steps": [
      {
        "step_number": 1,
        "description": ""
      }
    ]
  }
}

Requirements:
- Include 5 to 8 realistic device components.
- Include 6 to 10 setup or troubleshooting steps.
- Beginner friendly explanations.
- No markdown.
- No code block.
- Valid JSON only.
`;

    const aiResponse = await client.responses.create({

      model: 'gpt-4.1-mini',

      input: prompt,
    });

    const text = aiResponse.output_text;

    let parsed;

    try {

      parsed = JSON.parse(text);

    } catch {

      return res.status(500).json({

        success: false,

        message: 'AI returned invalid JSON',
      });
    }

    // ===================================
    // INSERT DEVICE
    // ===================================

    const deviceInsert = await pool.query(

      `
      INSERT INTO devices
      (devicename, devicetype)
      VALUES ($1, $2)
      RETURNING *
      `,
      [
        parsed.device_name,
        parsed.device_type,
      ]
    );

    const device = deviceInsert.rows[0];

    // ===================================
    // INSERT COMPONENTS
    // ===================================

    for (const component of parsed.components) {

      await pool.query(

        `
        INSERT INTO components
        (deviceid, componentname, description)
        VALUES ($1, $2, $3)
        `,
        [
          device.deviceid,
          component.component_name,
          component.description,
        ]
      );
    }

    // ===================================
    // INSERT GUIDE
    // ===================================

    const guideInsert = await pool.query(

      `
      INSERT INTO guides
      (deviceid, title, datecreated)
      VALUES ($1, $2, CURRENT_DATE)
      RETURNING *
      `,
      [
        device.deviceid,
        parsed.guide.title,
      ]
    );

    const guide = guideInsert.rows[0];

    // ===================================
    // INSERT STEPS
    // ===================================

    for (const step of parsed.guide.steps) {

      await pool.query(

        `
        INSERT INTO steps
        (guideid, stepnumber, description)
        VALUES ($1, $2, $3)
        `,
        [
          guide.guideid,
          step.step_number,
          step.description,
        ]
      );
    }

    return res.status(201).json({

      success: true,

      source: 'ai_generated',

      device: {

        deviceid: device.deviceid,

        devicename: device.devicename,

        devicetype: device.devicetype,

        guideid: guide.guideid,

        guide_title: guide.title,
      },
    });

  } catch (error) {

    console.error(error);

    return res.status(500).json({

      success: false,

      message: 'Server Error',
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