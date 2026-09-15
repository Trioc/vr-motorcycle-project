using UnityEngine;
using UnityEngine.Video;

public class TimedObjectOnVideo : MonoBehaviour
{
    [Header("Assign in Inspector")]
    public VideoPlayer videoPlayer;   // 播 360° 影片的 VideoPlayer（Sphere 上）
    public GameObject targetObject;   // 要顯示 / 隱藏的物件（LampPointer）

    [Header("Timing (seconds)")]
    public double startTime = 5.0;    // 影片時間 >= 這個秒數時出現
    public double endTime = 10.0;     // 影片時間 > 這個秒數時消失

    public bool pauseVideoWhileShown = false;  // 出現時是否暫停影片

    bool _isShown = false;

    void Start()
    {
        if (targetObject != null)
            targetObject.SetActive(false);
    }

    void Update()
    {
        if (videoPlayer == null || targetObject == null)
            return;

        // 確認影片有在跑或至少準備好了
        if (!videoPlayer.isPrepared && !videoPlayer.isPlaying)
            return;

        double t = videoPlayer.time;
        bool shouldShow = (t >= startTime && t <= endTime);

        if (shouldShow && !_isShown)
        {
            // 進入顯示區間
            targetObject.SetActive(true);
            _isShown = true;

            if (pauseVideoWhileShown && videoPlayer.isPlaying)
                videoPlayer.Pause();
        }
        else if (!shouldShow && _isShown)
        {
            // 離開顯示區間
            targetObject.SetActive(false);
            _isShown = false;

            if (pauseVideoWhileShown && !videoPlayer.isPlaying)
                videoPlayer.Play();
        }
    }
}
