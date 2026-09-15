using UnityEngine;
using UnityEngine.Video;
using UnityEngine.Events;

public class VRUIPopup : MonoBehaviour
{
    [Header("Assign in Inspector")]
    public GameObject panel;          // 指到 Canvas 下的 Panel
    public VideoPlayer videoPlayer;   // 指到 Sphere 上的 VideoPlayer，沒有也可留空
    public UnityEvent onConfirmed;    // 之後要串別的事件可以用

    void Start()
    {
        HidePanel();                  // 一開始先關掉面板
    }

    public void ShowPanel()
    {
        if (!panel) return;
        panel.SetActive(true);
        if (videoPlayer && videoPlayer.isPlaying)
            videoPlayer.Pause();
    }

    public void HidePanel()
    {
        if (!panel) return;
        panel.SetActive(false);
    }

    // 這個綁到 Button 的 OnClick
    public void Confirm()
    {
        HidePanel();
        if (videoPlayer && !videoPlayer.isPlaying)
            videoPlayer.Play();

        onConfirmed?.Invoke();
    }
}
