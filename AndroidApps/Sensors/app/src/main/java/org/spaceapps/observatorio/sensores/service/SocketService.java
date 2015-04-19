package org.spaceapps.observatorio.sensores.service;

/**
 * Created by Dennis on 12/04/2015.
 */
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;

import android.app.IntentService;
import android.app.Notification;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Intent;
import android.util.Log;
import android.widget.Toast;

public class SocketService extends IntentService {
    private NotificationManager notifMan;
    //private int NOTIFICATION = R.string.SERVICE_STARTED;

    ServerSocket server;
    Socket client;

    public SocketService() {
        super("SocketService");
    }

    @Override
    public void onCreate() {
    	Toast.makeText(this,"Servicio creado", Toast.LENGTH_SHORT).show();
    }

    @Override
    public boolean stopService(Intent intent) {
        try {
            if (client != null) {
                client.close();
                client = null;
            }
            if (server != null) {
                server.close();
                server = null;
            }
        } catch (IOException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        return super.stopService(intent);
    }

    @Override
    public int onStartCommand(Intent intenc, int flags, int idArranque) {
        return START_STICKY;
    }

    @Override
    public void onDestroy() {
        this.stopForeground(true);
    }


    @Override
    protected void onHandleIntent(Intent arg0) {
        BufferedReader input;
        PrintWriter output;

        try {
            server = new ServerSocket(8888);

            while(true) {
                client = server.accept();
                input = new BufferedReader(new InputStreamReader(client.getInputStream()));
                output = new PrintWriter(new OutputStreamWriter(client.getOutputStream()));
                String in = input.readLine();
                output.write(in);
//				System.out.println(in);
            }
        } catch (IOException e) {
            e.printStackTrace();
            Log.d("DEBUG", e.getMessage());
        }
    }

}