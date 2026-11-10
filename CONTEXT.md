shopee-express-app/
├── package.json                                  # Đã tạo mới, khai báo express và script "start": "node server.js"
├── server.js                                     # Express server (port 3000), serve /public, /data và GET /api/datasets, /api/health
├── data/
│   ├── Shopee_Simulated_Transactions.xlsx        # Dataset 1: 1.000 dòng (schema chuẩn Python)
│   └── Shopee_TransactionsNew.xlsx               # Dataset 2: 5.000 dòng (schema mới, đơn vị VND nguyên)
└── public/
    ├── index.html                                # Giao diện Dashboard chính, có dropdown chọn nhanh dataset từ server
    ├── style.css                                 # CSS hoàn chỉnh (tách từ style_2.css)
    └── script.js                                 # Toàn bộ logic DataLoader, ShopeePipeline, Visualizer, ReportGenerator