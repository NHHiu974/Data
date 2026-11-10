const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;

// Phục vụ file tĩnh giao diện từ thư mục public/
app.use(express.static(path.join(__dirname, 'public')));

// Dataset hiện nằm cạnh server.js, không nằm trong thư mục data/.
const datasetExtensions = new Set(['.xlsx', '.xls', '.csv']);

app.get('/api/datasets', (req, res) => {
    fs.readdir(__dirname, (err, files) => {
        if (err) return res.status(500).json({ error: 'Không thể liệt kê dataset' });
        const excelFiles = files.filter(f => datasetExtensions.has(path.extname(f).toLowerCase()));
        res.json(excelFiles);
    });
});

app.get('/data/:filename', (req, res, next) => {
    const filename = req.params.filename;
    if (path.basename(filename) !== filename || !datasetExtensions.has(path.extname(filename).toLowerCase())) {
        return res.sendStatus(404);
    }

    const filePath = path.join(__dirname, filename);
    fs.access(filePath, fs.constants.R_OK, err => {
        if (err) return res.sendStatus(404);
        res.sendFile(filePath, sendError => {
            if (sendError) next(sendError);
        });
    });
});

// API kiểm tra trạng thái server
app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', message: 'Shopee Analytics Express Server is running' });
});

app.listen(PORT, () => {
    console.log('====================================================');
    console.log(`Server Express đang chạy tại: http://localhost:${PORT}`);
    console.log('====================================================');
});