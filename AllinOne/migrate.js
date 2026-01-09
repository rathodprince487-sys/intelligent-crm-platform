const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const bcrypt = require('bcryptjs');

const dbPath = path.join(__dirname, 'database.sqlite');
const db = new sqlite3.Database(dbPath);

const COMMON_USER_ID = 999;
const COMMON_EMAIL = "common@company.com";
const COMMON_PASS = "common123";

db.serialize(async () => {
    console.log("🛠 Splitting Common vs Personal CRM...");

    // 1. Insert Common/Company User
    const hash = await bcrypt.hash(COMMON_PASS, 10);
    const now = new Date().toISOString();

    // Check if exists or insert
    db.run(`
        INSERT OR IGNORE INTO Users (id, name, email, password, createdAt, updatedAt)
        VALUES (?, ?, ?, ?, ?, ?)
    `, [COMMON_USER_ID, "Common CRM (Company)", COMMON_EMAIL, hash, now, now], (err) => {
        if (!err) console.log("✅ Common CRM User (ID 999) created.");
    });

    // 2. MOVE ALL EXISTING LEADS TO COMMON USER (ID 999)
    // Assumption: The leads recovered so far are company leads.
    // If you have added NEW personal leads in the last 10 mins, they will also be moved.
    // Let's assume everything currently in DB is "Common".
    db.run(`UPDATE Leads SET userId = ?`, [COMMON_USER_ID], function (err) {
        if (err) console.error("❌ Error moving leads:", err);
        else console.log(`✅ Moved ${this.changes} leads to Common CRM (ID 999).`);

        db.close();
    });
});
