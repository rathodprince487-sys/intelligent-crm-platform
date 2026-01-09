const { Sequelize, DataTypes } = require('sequelize');
const path = require('path');

const sequelize = new Sequelize({
    dialect: 'sqlite',
    storage: path.join(__dirname, 'database.sqlite'),
    logging: false
});

async function check() {
    try {
        const counts = await sequelize.query("SELECT userId, count(*) as count FROM Leads GROUP BY userId", { type: sequelize.QueryTypes.SELECT });
        console.log("--- LEADS COUNT BY USER ---");
        console.log(counts);
    } catch (e) {
        console.error("Error:", e);
    }
}

check();
