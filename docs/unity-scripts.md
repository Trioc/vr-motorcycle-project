# Unity 腳本與整合說明

收錄四支原始 C# 腳本及其 .meta，未修改行為。以下依靜態程式閱讀整理，尚未在 Unity 編譯或接上 VR 裝置驗證。

| 腳本 | 已實作行為 | Inspector 依賴 |
| --- | --- | --- |
| CountdownUI | Start 啟動倒數、更新文字，結束後隱藏面板及輸出日誌 | countdownText（TextMeshProUGUI）、panel、countdownTime |
| TimedPopup | 影片播放到指定秒數後，一次性顯示面板；可暫停影片，等待指定時長後關閉及恢復 | videoPlayer、panel、triggerTimeSec、showDurationSec、pauseVideo |
| TimedObjectOnVideo | 根據影片起訖秒數顯示／隱藏指定物件，可選擇暫停影片 | videoPlayer、targetObject、startTime、endTime、pauseVideoWhileShown |
| VRUIPopup | ShowPanel 顯示並暫停；Confirm 關閉、播放並呼叫 UnityEvent | panel、videoPlayer、onConfirmed；按鈕 OnClick 需綁 Confirm |

## 已知限制

- CountdownUI 的影片播放與場景切換僅為註解，沒有實際執行；不能寫成此腳本自動啟動完整實驗。文字或面板未綁定會產生空參考錯誤。
- TimedPopup 的 fired 不會於影片重播時重置；同一元件生命週期只觸發一次。WaitForSeconds 使用受 timeScale 影響的遊戲時間。
- TimedObjectOnVideo 的 pauseVideoWhileShown 預設為 false。若啟用，進入顯示區間後影片時間停住，通常無法靠自身越過 endTime，需外部機制恢復播放或改變時間；這是特定配置下的風險，未確認原場景是否啟用。
- VRUIPopup 的確認會在影片非播放狀態時呼叫 Play，沒有保存先前暫停原因。
- 多支腳本可控制同一 VideoPlayer，實際是否衝突取決於場景與事件綁定。
- 目前腳本未包含油門、轉向或車輛物理控制，不以此宣稱有可操控的機車模擬器。

## 尚未收錄

Scenes、影片、材質、XR／SteamVR 資產及 Inspector 綁定。原始 manifest 中 OpenVR 指向 Assets/SteamVR 下的本機 tgz；因此直接複製 manifest 並不能使這份展示包成為完整可執行專案。

## 展示定位

以 Unity 360° 影片式 VR 教學搭配視覺提示，另以 Python 進行危險感知點擊紀錄與時間評分。個人貢獻與研究分工見 README；未收錄真人姓名與原專案雲端識別資訊。
