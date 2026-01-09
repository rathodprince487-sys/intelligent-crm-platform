const { Sequelize, DataTypes } = require('sequelize');
const path = require('path');

// Initialize SQLite
const sequelize = new Sequelize({
    dialect: 'sqlite',
    storage: path.join(__dirname, 'database.sqlite'),
    logging: false
});

// Define User Model
const User = sequelize.define('User', {
    name: { type: DataTypes.STRING, allowNull: false },
    email: { type: DataTypes.STRING, allowNull: false, unique: true },
    password: { type: DataTypes.STRING, allowNull: false },
    role: { type: DataTypes.STRING, defaultValue: 'Intern' }, // Roles: 'Intern', 'HR'
    allowCommonAccess: { type: DataTypes.BOOLEAN, defaultValue: false } // HR controls this
});

// Define Lead Model
const Lead = sequelize.define('Lead', {
    businessName: { type: DataTypes.STRING, allowNull: false },
    contactName: DataTypes.STRING,
    address: DataTypes.STRING,
    phone: { type: DataTypes.STRING },
    email: DataTypes.STRING,
    query: DataTypes.STRING,
    location: DataTypes.STRING,

    // Enhanced Status List
    status: {
        type: DataTypes.STRING,
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
    lastFollowUpDate: DataTypes.DATEONLY,
    nextFollowUpDate: DataTypes.DATEONLY,
    meetingDate: DataTypes.DATEONLY,

    callNotes: DataTypes.TEXT,
    duplicateFound: { type: DataTypes.BOOLEAN, defaultValue: false },

    // Foreign Key
    userId: {
        type: DataTypes.INTEGER,
        allowNull: false
    }
});

// Define Execution Model
const Execution = sequelize.define('Execution', {
    query: DataTypes.STRING,
    location: DataTypes.STRING,
    date: DataTypes.DATE,
    leadsGenerated: DataTypes.INTEGER,
    status: DataTypes.STRING
});

// Relationships
User.hasMany(Lead, { foreignKey: 'userId', onDelete: 'CASCADE' });
Lead.belongsTo(User, { foreignKey: 'userId' });

// Sync database
const initDB = async () => {
    try {
        await sequelize.sync({ alter: true }); // Update schema structure
        console.log("✅ Database synced");
    } catch (error) {
        console.error("❌ Database sync failed:", error);
    }
};

module.exports = { sequelize, User, Lead, Execution, initDB };
