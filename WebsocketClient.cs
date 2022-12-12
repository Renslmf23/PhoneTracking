using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using WebSocketSharp;

public class WebsocketClient : MonoBehaviour
{
    public Transform phoneObject;
    private Vector3 position;
    WebSocket ws;
    private void Start() {
        ws = new WebSocket("ws://localhost:11225");
        ws.Connect();
        ws.OnMessage += (sender, e) => {
            //Debug.Log("Message Received from " + ((WebSocket)sender).Url + ", Data : " + e.Data);
            string posString = e.Data;
            posString = posString.Replace("(", "");
            posString = posString.Replace(")", "");
            print(posString);
            var data = posString.Split(",");
        
            position.x = float.Parse(data[0])/60;
            position.y = float.Parse(data[1])/60;
            Debug.Log(data);
        };
    }
    private void Update() {
        if (ws == null) {
            return;
        }
        phoneObject.position = position;
        Debug.Log(position);

    }

	private void OnApplicationQuit() {
        ws.Close();
	}
}
