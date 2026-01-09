const express = require("express");
const axios = require("axios");
const cors = require("cors");
const { parse } = require("csv-parse/sync");
const { initDB, User, Lead, Execution, sequelize } = require("./database");
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");

// ✅ App MUST be initialized first
const app = express();
const SECRET_KEY = "my_super_secret_key_shhh_dont_tell_anyone_or_i_will_cry"; // Env var in prod

// ------------------------------
// Middleware
// ------------------------------
app.use(cors());
app.use(express.json());

// 🔐 Auth Middleware
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

  if (!token) return res.sendStatus(401);

  jwt.verify(token, SECRET_KEY, (err, user) => {
    if (err) return res.sendStatus(403);
    req.user = user;
    next();
  });
};

// ------------------------------
// Database Initialization
// ------------------------------
initDB().then(async () => {
  // Seed HR User
  try {
    const hrEmail = "vyonish@shdpixel.com";
    const exists = await User.findOne({ where: { email: hrEmail } });
    if (!exists) {
      const hashedPassword = await bcrypt.hash("admin", 10);
      await User.create({
        name: "Vyonish Momaya",
        email: hrEmail,
        password: hashedPassword,
        role: "HR",
        allowCommonAccess: true
      });
      console.log("🚀 HR User 'Vyonish Momaya' created (vyonish@shdpixel.com / admin)");
    }
  } catch (e) { console.error("Seeding Error:", e); }
});

// ------------------------------
// Health check
// ------------------------------
app.get("/", (req, res) => {
  res.send("BackEnd PERSONAL CRM v2.1 (Secured) is running 🚀");
});


// ------------------------------
// 🔐 AUTH ROUTES
// ------------------------------

// REGISTER (Public - Optional, maybe remove if HR only?)
app.post("/auth/register", async (req, res) => {
  try {
    const { name, email, password } = req.body;
    if (!name || !email || !password) return res.status(400).json({ error: "Missing fields" });

    const hashedPassword = await bcrypt.hash(password, 10);
    const user = await User.create({ name, email, password: hashedPassword });

    res.status(201).json({ message: "User registered successfully" });
  } catch (error) {
    res.status(400).json({ error: "Email already exists or invalid data" });
  }
});

// LOGIN
app.post("/auth/login", async (req, res) => {
  try {
    const { email, password } = req.body;
    const user = await User.findOne({ where: { email } });

    if (!user) return res.status(400).json({ error: "User not found" });

    const validPassword = await bcrypt.compare(password, user.password);
    if (!validPassword) return res.status(403).json({ error: "Invalid credentials" });

    // Create Token
    const token = jwt.sign(
      { id: user.id, email: user.email, name: user.name, role: user.role, allowCommonAccess: user.allowCommonAccess },
      SECRET_KEY,
      { expiresIn: '24h' }
    );

    res.json({ token, user: { id: user.id, name: user.name, email: user.email, role: user.role, allowCommonAccess: user.allowCommonAccess } });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});


// ------------------------------
// 👥 USER MANAGEMENT (HR ONLY)
// ------------------------------
app.post("/users/create", authenticateToken, async (req, res) => {
  // Only HR can create users
  if (req.user.role !== 'HR') return res.status(403).json({ error: "Access Denied" });

  try {
    const { name, email, password, role, allowCommonAccess } = req.body;

    // Validation
    if (!name || !email || !password) return res.status(400).json({ error: "Missing required fields" });

    // Hash Password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Create User
    const newUser = await User.create({
      name,
      email,
      password: hashedPassword,
      role: role || 'Intern',
      allowCommonAccess: allowCommonAccess || false
    });

    res.status(201).json({ message: "User created successfully", userId: newUser.id });

  } catch (e) {
    console.error("Create user error:", e);
    res.status(500).json({ error: e.message || "Failed to create user" });
  }
});



// ------------------------------
// 🔥 LEAD GENERATION & SAVE (Authenticated)
// ------------------------------
app.post("/lead-gen", authenticateToken, async (req, res) => {
  const { query, location } = req.body;
  const userId = req.user.id; // From Token

  if (!query || !location) {
    return res.status(400).json({ error: "Query and location are required" });
  }

  try {
    // 1. Call n8n
    const response = await axios.post(
      N8N_LEAD_GEN_WEBHOOK,
      { query, location },
      { timeout: 120000, responseType: "arraybuffer" }
    );

    const csvData = response.data;

    // 2. Log Execution (Global log for now, could be scoped)
    const execution = await Execution.create({
      query,
      location,
      date: new Date(),
      leadsGenerated: 0,
      status: "Success"
    });

    // 3. Parse and Save Leads (SCOPED TO USER)
    try {
      const records = parse(csvData, { columns: true, skip_empty_lines: true, trim: true });
      let count = 0;
      for (const record of records) {
        const businessName = record["Business Name"] || record["name"] || "Unknown";
        const phone = record["Phone"] || record["phone"] || null;

        // Deduplication (Scoped to User?)
        // Ideally dedupe globally to avoid spamming same business, OR scoped to user.
        // Requirement: "Duplicate checker must work ONLY within user's data" -> Scoped.

        const whereClause = { userId }; // Only check THIS user's duplicates
        if (phone) whereClause.phone = phone;
        else whereClause.businessName = businessName;

        const [lead, created] = await Lead.findOrCreate({
          where: whereClause,
          defaults: {
            businessName,
            address: record["Address"] || record["address"],
            phone,
            email: record["Email"] || record["email"],
            query,
            location,
            status: "Generated",
            userId: userId // 👈 IMPORTANT
          }
        });

        if (created) count++;
      }

      await execution.update({ leadsGenerated: count });
      console.log(`✅ Saved ${count} new leads for User ${userId}.`);

    } catch (parseError) {
      console.error("❌ CSV Parsing Failed:", parseError.message);
    }

    // 4. Return CSV
    res.setHeader("Content-Type", "text/csv");
    res.setHeader("Content-Disposition", `attachment; filename=${query}_${location}_leads.csv`);
    res.send(Buffer.from(csvData));

  } catch (error) {
    console.error("❌ Lead gen error:", error.message);
    res.status(500).json({ error: "Lead generation failed" });
  }
});

// ------------------------------
// 📊 CRM API ENDPOINTS (Authenticated)
// ------------------------------

const ADMIN_EMAIL = "satyajeetrathod5@gmail.com";
const COMMON_USER_ID = 999;

// Get All Users (For HR to see list of interns)
app.get("/users", authenticateToken, async (req, res) => {
  try {
    if (req.user.role !== 'HR') {
      return res.status(403).json({ error: "Access denied" });
    }
    const users = await User.findAll({
      attributes: ['id', 'name', 'email', 'role'] // No passwords
    });
    res.json(users);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// Get All Leads (Scoped by Toggle)
app.get("/leads", authenticateToken, async (req, res) => {
  try {
    const { status, scope, targetUserId } = req.query; // Scope: 'common' or 'personal' (default)
    let where = {};

    if (scope === 'common') {
      // PERMISSION CHECK for Common Data
      // HR always has access. Interns need explicit permission.
      if (req.user.role !== 'HR' && !req.user.allowCommonAccess) {
        return res.status(403).json({ error: "Access to Team Leads denied by Administrator." });
      }
      where.userId = COMMON_USER_ID;
    } else if (scope === 'all' && req.user.role === 'HR') {
      // HR View: All Interns -> Filter by user selection if provided
      if (targetUserId) {
        where.userId = targetUserId;
      }
      // Else show everything (or nothing until selected? User request implies showing list first)
      // "in all interns he should see the list of pepole who are interns and then when he clickl on the name he should see that persons personal CRM"
      // This means we might not use 'all' to fetch leads directly, but we support targetUserId.

    } else {
      // Personal (Default)
      // Personal (Default) - "My Leads" means MY leads, even for HR.
      where.userId = req.user.id;
    }

    if (status) where.status = status;

    // If Admin wants to see truly everything (Debug), they can query differently, 
    // but for the UI toggle "Common vs Personal", this is cleaner.

    const leads = await Lead.findAll({
      where,
      order: [['createdAt', 'DESC']],
      include: [{ model: User, attributes: ['name'] }]
    });
    res.json(leads);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// Update Lead (User can edit their own or Common leads)
app.put("/leads/:id", authenticateToken, async (req, res) => {
  try {
    const { id } = req.params;

    // Allow editing if:
    // 1. It belongs to me
    // 2. OR It belongs to Common
    // 3. OR I am Admin
    const lead = await Lead.findByPk(id);
    if (!lead) return res.status(404).json({ error: "Lead not found" });

    const isOwner = lead.userId === req.user.id;
    const isCommon = lead.userId === COMMON_USER_ID;
    const isAdmin = req.user.email === ADMIN_EMAIL;

    if (!isOwner && !isCommon && !isAdmin) {
      return res.status(403).json({ error: "Unauthorized" });
    }

    await lead.update(req.body);

    if (req.body.meetingDate) {
      triggerCalendarEvent(lead);
    }

    res.json(lead);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// Create Lead (To Personal or Common)
app.post("/leads", authenticateToken, async (req, res) => {
  try {
    if (!req.body.businessName) req.body.businessName = "New Lead";

    // Determine Target User ID
    // If frontend sends 'scope' or 'targetUserId', use it. Else default to self.
    let targetUserId = req.user.id;

    if (req.body.targetScope === 'common') {
      targetUserId = COMMON_USER_ID;
    }

    const newLeadData = { ...req.body, userId: targetUserId };
    const lead = await Lead.create(newLeadData);

    if (req.body.meetingDate) {
      triggerCalendarEvent(lead);
    }

    res.json(lead);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// Delete Lead
app.delete("/leads/:id", authenticateToken, async (req, res) => {
  try {
    const { id } = req.params;
    const lead = await Lead.findByPk(id);
    if (!lead) return res.status(404).json({ error: "Lead not found" });

    const isOwner = lead.userId === req.user.id;
    const isCommon = lead.userId === COMMON_USER_ID;
    const isAdmin = req.user.email === ADMIN_EMAIL;

    if (!isOwner && !isCommon && !isAdmin) {
      return res.status(403).json({ error: "Unauthorized" });
    }

    await lead.destroy();
    res.json({ success: true });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// Get Stats (Based on Scope)
app.get("/stats", authenticateToken, async (req, res) => {
  try {
    const { scope } = req.query;
    let where = {};

    if (scope === 'common') {
      where.userId = COMMON_USER_ID;
    } else {
      where.userId = req.user.id;
    }

    const totalLeads = await Lead.count({ where });
    const leadsByStatus = await Lead.findAll({
      where,
      attributes: ['status', [sequelize.fn('COUNT', sequelize.col('status')), 'count']],
      group: ['status']
    });

    const stats = { total: totalLeads, breakdown: {} };
    leadsByStatus.forEach(item => {
      stats.breakdown[item.status] = item.dataValues.count;
    });
    res.json(stats);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// Get Executions (Public or Admin? For now let's make it public or maybe auth optional)
// Typically Execution logs are system-wide. Let's keep it open or just limit access.
// For Personal CRM, maybe only show executions trigger by user? 
// Current DB schema for Execution doesn't have userId. We leave it as global for now.
app.get("/executions", async (req, res) => {
  try {
    const history = await Execution.findAll({ order: [['date', 'DESC']] });
    res.json(history);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// ------------------------------
// Server start
// ------------------------------
app.listen(3000, () => {
  console.log("✅ Backend PERSONAL CRM v2.1 running on http://localhost:3000");
});
