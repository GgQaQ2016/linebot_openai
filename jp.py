%%{init: {'theme': 'default', 'themeVariables': {
  "primaryColor": "#A8C0BA",       /* 柔和青灰調 */
  "secondaryColor": "#E8E0D5",     /* 溫暖奶油色 */
  "tertiaryColor": "#F3D9B1",      /* 溫潤米色 */
  "lineColor": "#BFB1A8",          /* 淡雅灰棕色 */
  "fontFamily": "Georgia, serif",  /* 文青風字型 */
  "fontSize": "14px",
  "titleFontSize": "20px"
}}}%%
gantt
    title 兩個月研究計畫 - 資料收集、需求分析與系統原型開發（8 週）
    dateFormat  YYYY-MM-DD
    axisFormat  %m/%d
    section 資料收集與需求分析
    資料收集與初步確認      :done,    d1, 2025-04-01, 7d
    需求分析與技術選型      :done,    d2, 2025-04-08, 7d
    section 數據預處理與向量化
    資料清洗與標準化        :done,    d3, 2025-04-15, 7d
    向量化處理與索引建立    :done,    d4, 2025-04-22, 7d
    section RAG 系統原型開發
    系統架構設計與原型搭建  :done,    d5, 2025-04-29, 7d
    重排序與生成模組集成    :done,    d6, 2025-05-06, 7d
    section 初步實驗與效能評估
    初步實驗與性能測試      :active,  d7, 2025-05-13, 7d
    數據分析與系統優化      :active,  d8, 2025-05-20, 7d
