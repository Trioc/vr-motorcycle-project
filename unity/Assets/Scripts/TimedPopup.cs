using System.Collections;
using UnityEngine;
using UnityEngine.Video;

public class TimedPopup : MonoBehaviour
{
    [Header("Assign in Inspector")]
    public VideoPlayer videoPlayer;    // 播 360 影片的 VideoPlayer（在 Sphere 上）
    public GameObject panel;          // Canvas 底下的 Panel

    [Header("Timing")]
    public double triggerTimeSec = 10.0;   // 影片播到幾秒時出現
    public float showDurationSec = 3.0f;   // 視窗停留幾秒
    public bool pauseVideo = true;         // 出現時是否暫停影片

    bool fired = false;

    void Start()
    {
        // 一開始先關掉視窗
        if (panel != null) panel.SetActive(false);
    }

    void Update()
    {
        if (fired) return;
        if (videoPlayer == null || panel == null) return;
        if (!videoPlayer.isPlaying) return;

        // 當影片時間 >= 觸發時間，就開始顯示視窗
        if (videoPlayer.time >= triggerTimeSec)
        {
            fired = true;
            StartCoroutine(ShowAndHide());
        }
    }

    IEnumerator ShowAndHide()
    {
        if (pauseVideo && videoPlayer.isPlaying)
            videoPlayer.Pause();

        panel.SetActive(true);

        yield return new WaitForSeconds(showDurationSec);

        panel.SetActive(false);

        if (pauseVideo && !videoPlayer.isPlaying)
            videoPlayer.Play();
    }
}
