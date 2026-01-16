const { Sequelize, DataTypes } = require('sequelize');
const path = require('path');

// Initialize SQLite
const sequelize = new Sequelize({
    dialect: 'sqlite',
    storage: path.join(__dirname, 'database.sqlite'),
    logging: false
});

// Define Lead Model
const Lead = sequelize.define('Lead', {
    businessName: { type: DataTypes.STRING, allowNull: false },
    contactName: DataTypes.STRING, // New
    address: DataTypes.STRING,
    phone: { type: DataTypes.STRING },
    email: DataTypes.STRING,
    query: DataTypes.STRING,
    location: DataTypes.STRING,
    source: DataTypes.STRING,

    // Enhanced Status List
    status: {
        type: DataTypes.STRING, // Changed to STRING to allow flexibility or extended ENUM
        defaultValue: 'Generated'
    },

    // New Fields
    priority: {
        type: DataTypes.ENUM('HOT', 'WARM', 'COLD'),
        defaultValue: 'WARM'
    },
    calledBy: DataTypes.STRING,
    meetingBy: DataTypes.STRING,
    closedBy: DataTypes.STRING,
    lastFollowUpDate: DataTypes.DATEONLY, // Date only for easier grid view
    lastFollowUpDate: DataTypes.DATEONLY, // Date only for easier grid view
    nextFollowUpDate: DataTypes.DATEONLY,
    meetingDate: DataTypes.DATEONLY,

    callNotes: DataTypes.TEXT,
    duplicateFound: { type: DataTypes.BOOLEAN, defaultValue: false }
});

// Define Execution Model (Log of runs)
const Execution = sequelize.define('Execution', {
    name: DataTypes.STRING,
    query: DataTypes.STRING,
    location: DataTypes.STRING,
    date: DataTypes.DATE,
    leadsGenerated: DataTypes.INTEGER,
    status: DataTypes.STRING,
    fileContent: DataTypes.TEXT
});

// Sync database
const initDB = async () => {
    try {
        await sequelize.sync({ alter: true });
        console.log("✅ Database synced");
    } catch (error) {
        console.error("❌ Database sync failed:", error);
    }
};

module.exports = { sequelize, Lead, Execution, initDB };
