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
initDB().then(async () => {
  // SEED DUMMY DATA ON STARTUP
  try {
    const count = await Lead.count();
    if (count === 0) {
      console.log('🌱 Database empty! Seeding dummy data...');

      const dummyLeads = [
        {
          businessName: "ABC Dental Clinic",
          phone: "+1-555-0101",
          address: "123 Main St, New York, NY 10001",
          website: "https://abcdental.example.com",
          email: "contact@abcdental.example.com",
          status: "Qualified",
          notes: "Interested in premium CRM features",
          assignedTo: "John Doe",
          dealValue: 5000,
          source: "Google Maps"
        },
        {
          businessName: "XYZ Healthcare Solutions",
          phone: "+1-555-0102",
          address: "456 Oak Ave, Los Angeles, CA 90001",
          website: "https://xyzhealthcare.example.com",
          email: "info@xyzhealthcare.example.com",
          status: "Contacted",
          notes: "Follow up next week",
          assignedTo: "Jane Smith",
          dealValue: 8500,
          source: "LinkedIn"
        },
        {
          businessName: "MediCare Plus",
          phone: "+1-555-0103",
          address: "789 Pine Rd, Chicago, IL 60601",
          website: "https://medicareplus.example.com",
          email: "sales@medicareplus.example.com",
          status: "Meeting Scheduled",
          notes: "Demo scheduled for next Monday",
          assignedTo: "John Doe",
          dealValue: 12000,
          source: "Referral",
          meetingDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
        },
        {
          businessName: "HealthFirst Diagnostics",
          phone: "+1-555-0104",
          address: "321 Elm St, Houston, TX 77001",
          website: "https://healthfirst.example.com",
          email: "contact@healthfirst.example.com",
          status: "Proposal Sent",
          notes: "Waiting for decision from management",
          assignedTo: "Jane Smith",
          dealValue: 15000,
          source: "Google Maps"
        },
        {
          businessName: "SmileCare Dentistry",
          phone: "+1-555-0105",
          address: "654 Maple Dr, Phoenix, AZ 85001",
          website: "https://smilecare.example.com",
          email: "admin@smilecare.example.com",
          status: "Won",
          notes: "Deal closed! Onboarding in progress",
          assignedTo: "John Doe",
          dealValue: 20000,
          source: "Cold Email",
          lastContacted: new Date()
        },
        {
          businessName: "City Medical Center",
          phone: "+1-555-0106",
          address: "987 Cedar Ln, Philadelphia, PA 19101",
          website: "https://citymedical.example.com",
          email: "info@citymedical.example.com",
          status: "Generated",
          notes: "New lead from scraper",
          source: "Google Maps"
        },
        {
          businessName: "Wellness Clinic Group",
          phone: "+1-555-0107",
          address: "147 Birch Blvd, San Antonio, TX 78201",
          website: "https://wellnessgroup.example.com",
          email: "contact@wellnessgroup.example.com",
          status: "Qualified",
          notes: "High potential client",
          assignedTo: "Jane Smith",
          dealValue: 7500,
          source: "Website"
        },
        {
          businessName: "TechCorp Solutions",
          phone: "+1-555-0108",
          address: "101 Tech Way, San Francisco, CA 94105",
          website: "https://techcorp.example.com",
          email: "sales@techcorp.example.com",
          status: "Negotiation",
          notes: "Discussing contract terms",
          assignedTo: "Michael Brown",
          dealValue: 50000,
          source: "Conference"
        },
        {
          businessName: "Global Trade Inc.",
          phone: "+1-555-0109",
          address: "202 Market St, London, UK",
          website: "https://globaltrade.example.com",
          email: "contact@globaltrade.example.com",
          status: "New",
          notes: "Interested in export services",
          source: "Web Form"
        },
        {
          businessName: "Green Energy Co.",
          phone: "+1-555-0110",
          address: "303 Solar Blvd, Berlin, Germany",
          website: "https://greenenergy.example.com",
          email: "info@greenenergy.example.com",
          status: "Generated",
          notes: "Potential partner for renewable projects",
          source: "LinkedIn"
        }
      ];

      await Lead.bulkCreate(dummyLeads);
      console.log('✅ Dummy data seeded successfully!');
    }
  } catch (error) {
    console.error('❌ Data seeding failed:', error);
  }
});

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
            status: "Generated",
            source: "Scraper"
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

// Bulk Create Leads (with Deduplication)
app.post("/leads/bulk", async (req, res) => {
  try {
    const leads = req.body; // Expecting array of lead objects
    if (!Array.isArray(leads)) {
      return res.status(400).json({ error: "Expected an array of leads" });
    }

    let createdCount = 0;
    const errors = [];

    for (const data of leads) {
      try {
        const businessName = data.businessName || "Unknown";
        const phone = data.phone || null;

        // Deduplication Logic
        const whereClause = {};
        if (phone && phone.length > 5) whereClause.phone = phone;
        else whereClause.businessName = businessName;

        const [lead, created] = await Lead.findOrCreate({
          where: whereClause,
          defaults: {
            ...data,
            businessName,
            status: data.status || "Generated",
            source: data.source || "Scraper"
          }
        });

        if (created) createdCount++;
      } catch (err) {
        errors.push({ name: data.businessName, error: err.message });
      }
    }

    res.json({
      success: true,
      count: createdCount,
      totalProcessed: leads.length,
      errors: errors.length > 0 ? errors : undefined
    });

  } catch (e) {
    console.error("Bulk create error:", e);
    res.status(500).json({ error: e.message });
  }
});

// Seed Dummy Leads (Manual Trigger)
app.post("/leads/seed", async (req, res) => {
  try {
    const dummyLeads = [
      {
        businessName: "ABC Dental Clinic",
        phone: "+1-555-0101",
        address: "123 Main St, New York, NY 10001",
        email: "contact@abcdental.example.com",
        status: "Qualified",
        priority: "HOT",
        notes: "Interested in premium CRM features",
        dealValue: 5000,
        source: "Google Maps"
      },
      {
        businessName: "XYZ Healthcare Solutions",
        phone: "+1-555-0102",
        address: "456 Oak Ave, Los Angeles, CA 90001",
        email: "info@xyzhealthcare.example.com",
        status: "Contacted",
        priority: "WARM",
        notes: "Follow up next week",
        dealValue: 8500,
        source: "LinkedIn"
      },
      {
        businessName: "MediCare Plus",
        phone: "+1-555-0103",
        address: "789 Pine Rd, Chicago, IL 60601",
        email: "sales@medicareplus.example.com",
        status: "Meeting set",
        priority: "HOT",
        notes: "Demo scheduled for next Monday",
        dealValue: 12000,
        source: "Referral",
        meetingDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
      },
      {
        businessName: "HealthFirst Diagnostics",
        phone: "+1-555-0104",
        address: "321 Elm St, Houston, TX 77001",
        email: "contact@healthfirst.example.com",
        status: "Proposal sent",
        priority: "WARM",
        notes: "Waiting for decision from management",
        dealValue: 15000,
        source: "Google Maps"
      },
      {
        businessName: "SmileCare Dentistry",
        phone: "+1-555-0105",
        address: "654 Maple Dr, Phoenix, AZ 85001",
        email: "admin@smilecare.example.com",
        status: "Closed - Won",
        priority: "COLD",
        notes: "Deal closed! Onboarding in progress",
        dealValue: 20000,
        source: "Cold Email"
      },
      {
        businessName: "City Medical Center",
        phone: "+1-555-0106",
        address: "987 Cedar Ln, Philadelphia, PA 19101",
        email: "info@citymedical.example.com",
        status: "Generated",
        priority: "WARM",
        notes: "New lead from scraper",
        source: "Google Maps"
      },
      {
        businessName: "Wellness Clinic Group",
        phone: "+1-555-0107",
        address: "147 Birch Blvd, San Antonio, TX 78201",
        email: "contact@wellnessgroup.example.com",
        status: "Qualified",
        priority: "HOT",
        notes: "High potential client",
        dealValue: 7500,
        source: "Website"
      },
      {
        businessName: "TechCorp Solutions",
        phone: "+1-555-0108",
        address: "101 Tech Way, San Francisco, CA 94105",
        email: "sales@techcorp.example.com",
        status: "Meeting set",
        priority: "HOT",
        notes: "Discussing contract terms",
        dealValue: 50000,
        source: "Conference"
      },
      {
        businessName: "Global Trade Inc.",
        phone: "+1-555-0109",
        address: "202 Market St, London, UK",
        email: "contact@globaltrade.example.com",
        status: "Generated",
        priority: "WARM",
        notes: "Interested in export services",
        source: "Web Form"
      },
      {
        businessName: "Green Energy Co.",
        phone: "+1-555-0110",
        address: "303 Solar Blvd, Berlin, Germany",
        email: "info@greenenergy.example.com",
        status: "Generated",
        priority: "COLD",
        notes: "Potential partner for renewable projects",
        source: "LinkedIn"
      }
    ];

    await Lead.bulkCreate(dummyLeads);
    console.log(`🌱 Manually seeded ${dummyLeads.length} leads.`);
    res.json({ success: true, count: dummyLeads.length });

  } catch (e) {
    console.error("Manual seed error:", e);
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
    const { name, fileContent } = req.body;
    const updateData = {};
    if (name) updateData.name = name;
    if (fileContent) updateData.fileContent = fileContent;

    await Execution.update(updateData, { where: { id } });
    res.json({ success: true });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

// ------------------------------
// Server start
// ------------------------------
app.listen(3000, "0.0.0.0", () => {
  console.log("✅ Backend running on http://0.0.0.0:3000");
});
