const express = require("express");
const axios = require("axios");
const cors = require("cors");
const { parse } = require("csv-parse/sync");
const { initDB, Lead, Execution, sequelize } = require("./database");

// ✅ App MUST be initialized first
const app = express();

// ------------------------------
// Middleware
// ------------------------------
app.use(cors());
app.use(express.json({ limit: '50mb' }));

// ------------------------------
// Database Initialization
// ------------------------------
initDB();

// ------------------------------
// Health check
// ------------------------------
app.get("/", (req, res) => {
  res.send("BackEnd CRM v2 is running 🚀");
});

const { google } = require('googleapis');
const path = require('path');

// ------------------------------
// 🔗 n8n Webhook URL
// ------------------------------
const N8N_LEAD_GEN_WEBHOOK = "http://localhost:5678/webhook-test/lead-gen";

// ------------------------------
// 📅 Google Calendar API Config
// ------------------------------
const KEYFILE_PATH = path.join(__dirname, 'service-account.json');
const CALENDAR_ID = 'primary'; // Or specific calendar ID if shared

// Helper to trigger Calendar Event DIRECTLY
async function triggerCalendarEvent(lead) {
  if (!lead.meetingDate) return;

  try {
    // 1. Authenticate
    const auth = new google.auth.GoogleAuth({
      keyFile: KEYFILE_PATH,
      scopes: ['https://www.googleapis.com/auth/calendar'],
    });

    // Check if keyfile exists (implicitly handled by auth.getClient but good to catch)
    try {
      await auth.getCredentials();
    } catch (err) {
      console.warn("⚠️ Google Calendar Auto-Set Skipped: 'service-account.json' missing or invalid.");
      console.warn("👉 Please download your Service Account Key from Google Cloud Console and save it as 'service-account.json' in this folder.");
      return;
    }

    const authClient = await auth.getClient();
    const calendar = google.calendar({ version: 'v3', auth: authClient });

    // 2. Prepare Event
    const title = `Meeting with ${lead.contactName || 'Lead'} (${lead.businessName || 'Company'})`;
    const description = `Phone: ${lead.phone || 'N/A'}\nAddress: ${lead.address || 'N/A'}\nNotes: ${lead.callNotes || ''}`;

    // Date formatting (SQLite is YYYY-MM-DD)
    const startDate = lead.meetingDate; // "2026-01-05"
    // For all day event, end date is start + 1 day
    // We need to calculate next day properly
    const dateObj = new Date(startDate);
    dateObj.setDate(dateObj.getDate() + 1);
    const nextDay = dateObj.toISOString().split('T')[0];

    const event = {
      summary: title,
      description: description,
      start: { date: startDate },
      end: { date: nextDay },
    };

    // 3. Insert Event
    const response = await calendar.events.insert({
      calendarId: CALENDAR_ID,
      resource: event,
    });

    console.log(`✅ Google Calendar Event Created: ${response.data.htmlLink}`);

  } catch (error) {
    console.error("❌ Google Calendar API Error:", error.message);
  }
}

// ------------------------------
// 🔥 LEAD GENERATION & SAVE
// ------------------------------
app.post("/lead-gen", async (req, res) => {
  const { query, location } = req.body;

  if (!query || !location) {
    return res.status(400).json({ error: "Query and location are required" });
  }

  try {
    // 1. Call n8n to scrape/generate data
    const response = await axios.post(
      N8N_LEAD_GEN_WEBHOOK,
      { query, location },
      {
        timeout: 120000,
        responseType: "arraybuffer", // Important for receiving CSV binary
      }
    );

    const csvData = response.data;

    // 2. Log Execution
    const execution = await Execution.create({
      name: `${query} in ${location}`,
      query,
      location,
      date: new Date(),
      leadsGenerated: 0,
      status: "Success",
      fileContent: csvData.toString()
    });

    // 3. Parse CSV and Save Leads (Async)
    try {
      const records = parse(csvData, {
        columns: true,
        skip_empty_lines: true,
        trim: true
      });

      let count = 0;
      for (const record of records) {
        // Map CSV fields to DB fields
        const businessName = record["Business Name"] || record["name"] || "Unknown";
        const phone = record["Phone"] || record["phone"] || null;

        // Deduplication
        const whereClause = {};
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
            status: "Generated"
          }
        });

        if (created) count++;
      }

      await execution.update({ leadsGenerated: count });
      console.log(`✅ Saved ${count} new leads to DB.`);

    } catch (parseError) {
      console.error("❌ CSV Parsing Failed:", parseError.message);
    }

    // 4. Return CSV
    res.setHeader("Content-Type", "text/csv");
    res.setHeader(
      "Content-Disposition",
      `attachment; filename=${query}_${location}_leads.csv`
    );
    res.send(Buffer.from(csvData));

  } catch (error) {
    console.error("❌ Lead gen error:", error.message);
    res.status(500).json({ error: "Lead generation failed" });
  }
});

// ------------------------------
// 📊 CRM API ENDPOINTS
// ------------------------------

// Get All Leads
app.get("/leads", async (req, res) => {
  try {
    const { status } = req.query;
    const where = status ? { status } : {};
    const leads = await Lead.findAll({
      where,
      order: [['createdAt', 'DESC']]
    });
    res.json(leads);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// Update Lead
app.put("/leads/:id", async (req, res) => {
  try {
    const { id } = req.params;
    const updateData = req.body;
    const [updated] = await Lead.update(updateData, { where: { id } });

    if (updated) {
      const lead = await Lead.findByPk(id);

      // AUTO-TRIGGER: If meetingDate changes/exists, trigger n8n
      if (req.body.meetingDate) {
        triggerCalendarEvent(lead);
      }

      res.json(lead);
    } else {
      res.status(404).json({ error: "Lead not found" });
    }
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// Create Lead
app.post("/leads", async (req, res) => {
  try {
    if (!req.body.businessName) {
      req.body.businessName = "New Lead";
    }
    const lead = await Lead.create(req.body);

    // Auto-trigger on creation too if date set
    if (req.body.meetingDate) {
      triggerCalendarEvent(lead);
    }

    res.json(lead);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// Delete Lead
app.delete("/leads/:id", async (req, res) => {
  try {
    const { id } = req.params;
    await Lead.destroy({ where: { id } });
    res.json({ success: true });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// Get Stats
app.get("/stats", async (req, res) => {
  try {
    const totalLeads = await Lead.count();
    const leadsByStatus = await Lead.findAll({
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

// Get Executions
// Get Executions
app.get("/executions", async (req, res) => {
  try {
    const history = await Execution.findAll({
      attributes: { exclude: ['fileContent'] },
      order: [['date', 'DESC']]
    });
    res.json(history);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// Create Execution (Manual Import)
app.post("/executions", async (req, res) => {
  try {
    const exec = await Execution.create({
      query: req.body.query,
      location: req.body.location,
      name: req.body.name || `${req.body.query} - ${req.body.location}`,
      date: new Date(),
      leadsGenerated: req.body.leadsGenerated || 0,
      status: req.body.status || "Success",
      fileContent: req.body.fileContent
    });
    res.json(exec);
  } catch (e) {
    console.error("Exec save error:", e.message);
    res.status(500).json({ error: e.message });
  }
});

// Get Single Execution with Data
app.get("/executions/:id", async (req, res) => {
  try {
    const { id } = req.params;
    const exec = await Execution.findByPk(id);
    if (!exec) return res.status(404).json({ error: "Not found" });
    res.json(exec);
  } catch (e) { res.status(500).json({ error: e.message }); }
});

// Rename Execution
app.put("/executions/:id", async (req, res) => {
  try {
    const { id } = req.params;
    const { name } = req.body;
    await Execution.update({ name }, { where: { id } });
    res.json({ success: true });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

// ------------------------------
// Server start
// ------------------------------
app.listen(3000, () => {
  console.log("✅ Backend running on http://localhost:3000");
});
