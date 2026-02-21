
# 七字仔電子書 - GitHub 網頁製作說明

這是一個將您的 ODT 文件轉換為網頁電子書的專案。目前已包含轉換後的網頁檔案。

## 檔案結構

### 核心檔案 (Core Files)
- `docs/`: 包含網頁電子書的所有檔案 (`index.html`, `style.css`, `script.js`, `images/`)。這是發佈到 GitHub Pages 的核心資料夾。
- `convert_odt_to_html.py`: **主要轉換程式**。用於從 ODT 文件重新生成網頁內容。若您修改了 ODT 檔，**只需執行此腳本**即可更新網頁。

### 輔助與偵錯工具 (Auxiliary & Debugging Tools)
*以下腳本僅供開發除錯使用，一般使用者**不需要**執行：*
- `inspect_odt_structure.py`: 用於檢查 ODT 文件的 XML 結構，輔助切分章節。
- `inspect_parallel.py`: 用於檢查歌詞並排後的 HTML 結構與段落分類（數字、標題或內容）。
- `analyze_section50.py`: 用於分析特定章節 (如 Section 50 目錄頁) 的內容結構。
- `check_fix.py`: 用於驗證特定歌詞編號或標籤不全的修復結果。
- `verify_sidebar.py`: **側邊欄驗證工具**。檢查生成的側邊欄標籤是否正確對應到章節內容，避免顯示空白。
- `locate_318.py`: **內容定位工具**。在生成後的 HTML 中搜尋特定關鍵字，並列出該關鍵字所在的章節及其包含的標題。
- `debug_odt.py`, `inspect_section2.py`, `inspect_section37.py`: 針對特定章節進行細部解析與標題偵錯的臨時腳本。

## 更新記錄 (Changelog)

### Version 2.6 (2026-02-21)
- **支援罕用與深字盤羅馬字 (CJK Extension/Rare Characters Support)**: 針對擴展區段（包含 Ext-A 到 Ext-F，如「𬦰，𠕆，𡳞，𪁎」等台語相關特殊漢字），為了徹底解決在手機與行動裝置上系統字體缺字造成的亂碼與豆腐塊問題，引進了涵蓋面極廣的開源字型**花園明朝體 (HanaMin / jsDelivr CDN API)**。這項技術以無形中自動退避 (Fallback) 的方式掛載於字體層尾端，確保任何罕見用字皆可正確渲染且不會拖慢網頁載入速度。
- **註腳 (Footnotes) 配置與優化**: 實作了 ODT 檔案中註腳的自動解析功能。註記編號顯示在對應文字的右上方，獨立的註解說明文字則自動附隨並排版在該段落（歌詞）的最尾端，同時採用稍微縮小的字體以便與主文做視覺區分，維持並排版面的整齊。

### Version 2.5 (2026-02-20)
- **響應式網頁設計 (Responsive Web Design, RWD)**: 全面升級手機與平板等行動裝置的閱讀體驗。
  - **行動版目錄 (Mobile Sidebar Navigation)**: 在螢幕寬度小於 `768px` 時，左側目錄會自動隱藏，畫面上方新增「☰ 目錄」漢堡選單按鈕。點擊後側邊欄會平滑滑出 (Slide-in) 並且背景會加入半透明遮罩 (Overlay)，使用者點擊目錄或點擊空白處可快速關閉目錄。
  - **歌詞對照疊加排版 (Mobile Parallel Layout Stack)**: 原本在桌面版左右並排的「漢羅對照歌詞」，在手機螢幕上會自動改為「上下疊加」模式 (先顯示首欄漢字，其後緊接次欄羅馬字排列)，擴展了文字的可用寬度，改善手機上文字被過度擠壓的問題。
  - **深色模式切換鍵優化**: 縮小並調整了 `Dark Mode` (深色模式) 切換按鈕在行動版上的留白區域尺寸與位置，進一步優化頂部空間利用。
- **行動版台羅拼音字體優化 (Mobile POJ Font Fallback)**: 針對手機版預設中文字型缺乏完整特殊拼音符號（如 `ⁿ`、`o͘`）與結合聲調符號（如 `e̍`、`i̍`）的問題，新增專屬字型退避機制 (`@font-face unicode-range`)，強制將所有羅馬字元與聲調符號轉由系統最佳相容的英文字型安全渲染，確保這些複合音標在手機上能完美結合且正確地對齊顯示。

### Version 2.4 (2026-02-20)
- **字體統一 (Unified Font)**: 全文頁面改用「芫荽 (Iansui)」字體，並確保漢羅對照歌詞的字體大小與行高一致，提升整體視覺質感。
- **逐行對齊優化 (Line-by-line Alignment)**: 針對漢羅並排歌詞實作逐行對齊，確保中文與羅馬字不僅段落對齊，每一行皆精確對應。

### Version 2.3 (2026-02-19)
- **版權頁獨立 (Copyright Page Separation)**: 新增自動偵測功能，將文件末尾的「版權頁」內容獨立為一個新章節，並新增至側邊欄目錄。
- **目錄合併優化**: 針對「目錄 寫作日期/發表刊物」進行特殊處理，避免其被錯誤分割為兩個章節。
- **表格樣式增強 (Table Styling)**: 改用標準 HTML 表格標籤渲染內容，並加強了邊框樣式 (2px solid) 與間距調整，提升閱讀體驗。
- **歌詞對齊修正**: 放寬了歌詞編號的偵測邏輯，修正了部分歌詞（如包含換行標籤的段落）未能正確並排顯示的問題，確保所有編號段落皆能對齊。
- **樣式調整**: 將章節標題下方的羅馬字副標題改為置中對齊 (Centered Alignment)，使其與標題更具一致性。
- **深色模式 (Dark Mode / Eye Protection)**: 全面將內容與背景區域調整為黑底白字，減少螢幕強光刺激，提升長時間閱讀的舒適度並保護眼睛。
- **字體統一 (Unified Font)**: 全文（包含漢羅對照歌詞）皆採用「芫荽 (Iansui)」字體，並統一了中英文歌詞的字體大小與行高，確保視覺上的整齊劃一。
- **對齊優化**: 強制設定漢羅對照歌詞為頂部對齊 (Align Start)，修正了因內容長度不同導致的錯位問題。
- **章節自動切分 (Automatic Section Splitting)**: 改進區段偵測邏輯，當一個原始區段包含多個標題時（例如將「服貿318事件」與「其它記錄」），程式會自動將其拆分為獨立章節，使目錄結構更精確。
- **側邊欄連結修復**: 優化標題提取邏輯，會自動過濾空白的標題標籤，解決了特定目錄連結顯示為空白的問題。

### Version 2.2 (2026-02-19)
- **優化章節分割 (Section Splitting)**: 改進了章節偵測邏輯，確保「封面」與「序言」能被正確視為獨立章節，並正確顯示於側邊欄導覽中。
- **程式碼註解**: 為轉換腳本 (`convert_odt_to_html.py`) 加入了詳細的中文註解與功能說明，方便日後維護。

### Version 2.1 (2026-02-14)
- **改進並排演算法 (Improved Parallel Algorithm)**: 增強對歌詞段落的自動偵測，支援更多種編號格式與間隔內容，確保歌詞對齊更精準。
- **新增側邊欄導覽 (Sidebar)**: 左側顯示目錄，點擊後右側才顯示對應內容。
- **優化並排顯示 (Parallel Layout)**: 自動偵測歌詞編號，將漢字與羅馬字自動排版為左右對照。
- **深色模式更新**: 支援側邊欄深色主題切換。

## 如何發佈到 GitHub Pages

1.  **建立 GitHub Repository**:
    -   登入 GitHub，建立一個新的 Repository (例如命名為 `ebook-chhit-ji-a`)。

2.  **上傳檔案**:
    -   將此資料夾內的所有檔案上傳到該 Repository。
    -   如果您使用 Git 命令列：
        ```bash
        git init
        git add .
        git commit -m "Sidebar update and layout fix"
        git branch -M main
        git remote add origin https://github.com/您的帳號/ebook-chhit-ji-a.git
        git push -u origin main
        ```

3.  **開啟 GitHub Pages**:
    -   在 Repository 頁面，進入 **Settings** > **Pages**。
    -   在 **Build and deployment** 下的 **Source** 選擇 `Deploy from a branch`。
    -   在 **Branch** 選擇 `main`，資料夾選擇 `/docs` (注意：這裡是選擇 `/docs`，因為我們的網頁檔案都在 docs 資料夾內)。
    -   儲存後，GitHub 會提供一個網址，您的電子書就可以瀏覽了！
    ![GITHUB SETTING.jpg](GITHUB%20SETTING.jpg)

## 如何更新內容

1.  修改您的 ODT 文件 (`merged_2026_1_17 libreoffice.odt`)。
2.  執行轉換腳本:
    ```bash
    python convert_odt_to_html.py
    ```
3.  將更新後的 `docs/` 資料夾內容推送到 GitHub。
