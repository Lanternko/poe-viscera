# Wickerman 臟器 Tier List

PoE 3.30 Covens 的 Wickerman 臟器（Viscera）價格分級，介面仿 Atlas。

- 價格：GitHub Actions 每小時抓 poe.ninja，重建後部署到 GitHub Pages。
- 靜態資料（`dl/us.html`、`dl/tw.html` 來自 poedb；`dl/items.json`、`dl/twitems.json` 來自官方 Trade API；`img/` 圖示）只在新賽季或改版時手動更新。
- 換賽季：改 `.github/workflows/update.yml` 的 `LEAGUE`，以及 `py/template.html` 裡 Trade 連結的聯盟名稱（`Covens`／`巫影密會`）。

本機建置：

```bash
python py/parse.py . && python py/build.py . _site/index.html
```
