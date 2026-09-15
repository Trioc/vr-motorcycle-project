using UnityEngine;
using TMPro;
using System.Collections;

public class CountdownUI : MonoBehaviour
{
    public TextMeshProUGUI countdownText;
    public GameObject panel; // 倒數視窗的 UI Panel
    public int countdownTime = 10;

    void Start()
    {
        StartCoroutine(StartCountdown());
    }

    IEnumerator StartCountdown()
    {
        int timeLeft = countdownTime;

        while (timeLeft > 0)
        {
            countdownText.text = $"實驗將在 {timeLeft} 秒後自動開始。";
            yield return new WaitForSeconds(1f);
            timeLeft--;
        }

        countdownText.text = "實驗即將開始…";

        yield return new WaitForSeconds(0.5f);

        // 倒數完成 → 自動開始實驗
        OnCountdownFinished();
    }

    void OnCountdownFinished()
    {
        // 1. 你可以選擇隱藏視窗
        panel.SetActive(false);

        // 2. 或開始播放 360° 影片
        // yourVideoPlayer.Play();

        // 3. 或切換到正式場景
        // SceneManager.LoadScene("MainExperiment");

        // 依你需求填進去
        Debug.Log("倒數結束，開始實驗");
    }
}
