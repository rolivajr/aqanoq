package org.spaceapps.observatorio.sensores.service;
/**
 * Created by Dennis on 11/04/2015.
 */
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.hardware.GeomagneticField;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.IBinder;
import android.os.PowerManager;
import android.util.Log;
import android.widget.Toast;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.PrintStream;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.UnknownHostException;

public class SensorService extends Service implements SensorEventListener {
    // Manejador de sensores
    // Sensor adapter
    SensorManager mSensores;

    // Sensores y arreglos para sensores
    // Individual sensors and arrays for sensor values
    Sensor sMag; //Magnetómetro
    Sensor sGir; //Giroscopio
    Sensor sAce; //Acelerómetro
    Sensor sRot; //Orientación

    float[] sMagValues;
    float[] sGirValues;
    float[] sAceValues;
    float[] sRotValues;
    float[] orientation;

    // Configuracion del servidor
    // Server socket configuration
    private final int SERVER_PORT = 7778;

    // Server and Socket variables
    Socket client;
    ServerSocket server;

    // Status para monitor de sensores
    // Status for sensor monitor
    boolean monitorStarted;

    // Variables para filtro de media movil
    // Low pass filter variables
    float[] orientationProm, orientationFinal;
    int sampleCount;
    private final int SAMPLES_FILTER = 100;


    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    @Override
    public void onCreate() {
        super.onCreate();

        // Obtener los sensores
        // Obtain the sensors
        mSensores = (SensorManager) getApplicationContext().getSystemService(SENSOR_SERVICE);
        sMag = mSensores.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD);
        sGir = mSensores.getDefaultSensor(Sensor.TYPE_GYROSCOPE);
        sAce = mSensores.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);

        // Agregar listeners para los sensores
        // Add sensor listeners
        mSensores.registerListener(this, sMag, SensorManager.SENSOR_DELAY_NORMAL);
        mSensores.registerListener(this, sGir, SensorManager.SENSOR_DELAY_NORMAL);
        mSensores.registerListener(this, sAce, SensorManager.SENSOR_DELAY_NORMAL);

        // Inicializar el filtro
        // Initialize the filter
        sampleCount = 0;
        orientationProm = new float[3];
        orientationFinal = new float[3];
        cleanProm();

        // Iniciar el monitor de sensores
        // Initiate the sensor monitor
        PowerManager pm = (PowerManager)getSystemService(Context.POWER_SERVICE);
        startMonitor();
        Toast.makeText(this,"Servicio creado", Toast.LENGTH_SHORT).show();
    }


    @Override
    public void onDestroy() {
        mSensores.unregisterListener(this, sMag);
        mSensores.unregisterListener(this,sGir);
        mSensores.unregisterListener(this,sAce);
        monitorStarted = false;
        Toast.makeText(this,"Servicio detenido", Toast.LENGTH_SHORT).show();
        super.onDestroy();
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {

        //Toast.makeText(this,"Iniciando servicio...", Toast.LENGTH_SHORT).show();
        //Log.d("SPACEAPPS", "onStartCommand");

        super.onStartCommand(intent,flags,startId);
        return START_STICKY;
    }

    @Override
    public void onSensorChanged(SensorEvent event) {
        if(event.sensor.equals(sMag)){
            sMagValues = event.values;
        }else if(event.sensor.equals(sGir)){
            sGirValues = event.values;
        }else if(event.sensor.equals(sAce)) {
            sAceValues = event.values;
        }else if(event.sensor.equals(sRot)){
            sRotValues = event.values;
        }

        // Obtener la matriz de rotacion para convertir vectores del sistema local al global
        // Obtain the rotation matrix
        float[] R = new float[9];
        float[] I = new float[9];
        if(sAceValues != null && sMagValues != null) {
            SensorManager.getRotationMatrix(R, I, sAceValues, sMagValues);

            // Obtener los angulos de orientacion
            // Get the orientation
            orientation = new float[3];
            SensorManager.getOrientation(R, orientation);

            // Convertir los ángulos a grados sexagesimales
            // Conversion to degrees
            orientation[0] = -orientation[0] * (180 / 3.141592f);
            orientation[1] = orientation[1] * (180 / 3.141592f);
            orientation[2] = orientation[2] * (180 / 3.141592f);

            // Aplicar el filtro de media movil a los angulos
            // Apply filter to data
            makeProm(orientation);
        }
    }

    /**
     * Función para calcular el promedio. Cuando se alcanzan SAMPLES_FILTER se actualizan los valores
     *
     * Method to apply average filter. When sampleCount equal SAMPLES_FILTER data is updated.
     *
     * @param orientation Arreglo de 3 valores con los angulos de orientación global
     *                    Array of length 3 that holds global orientation angles.
     */
    private void makeProm(float [] orientation) {
        // Acumular valores de sensores
        // Accumulator
        for (int i = 0; i < 3; i++) {
            orientationProm[i] += orientation[i];
        }

        sampleCount++;

        if (sampleCount == SAMPLES_FILTER) {
            // Reiniciar el contador de muestras
            // Restart sample counter
            sampleCount = 0;

            // Obtener el promedio
            // Get the average
            for (int i = 0; i < 3; i++) {
                orientationFinal[i] = orientationProm[i] / SAMPLES_FILTER;
            }

            // Limpiar el promedio
            // Clean the dummy variables for average
            cleanProm();
        }
    }

    /**
     * Función para limpiar los valores del filtro de media movil
     * Method to restart values of the filter.
     */
    private void cleanProm() {
        for (int i = 0; i < 3; i++) {
            orientationProm[i] = 0;
        }
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) {

    }

    private void startMonitor() {
        if(monitorStarted)
            return;

        Runnable r = new Runnable() {

            @Override
            public void run() {
                ObjectInputStream input;
                ObjectOutputStream output;

                try {
                    // Initiate the server socket
                    server = new ServerSocket(SERVER_PORT);
                    while(monitorStarted){
                        client = server.accept();
                        // Get the InputStream and OutputStream
                        BufferedReader entrada = new BufferedReader(new InputStreamReader(client.getInputStream()));
                        PrintWriter salida = new PrintWriter(new OutputStreamWriter(client.getOutputStream()), true);
                        String datos = entrada.readLine();

                        // Classify the input
                        switch(datos) {
                            case "m":
                                datos = valuesString(sMagValues);
                                break;
                            case "r":
                                datos = valuesString(orientationFinal);
                                break;
                            case "a":
                                datos = valuesString(sAceValues);
                                break;
                            case "g":
                                datos = valuesString(sGirValues);
                                break;
                            default:
                                datos = "#";
                                break;
                        }

                        // Return sensor data
                        salida.println(datos);
                        client.close();
                    }
                } catch (IOException e) {
                    e.printStackTrace();
                    //Toast.makeText(SensorService.this,e.getMessage(), Toast.LENGTH_SHORT).show();
                }

            }
        };

        // Start the sensor monitor
        new Thread(r).start();
        monitorStarted = true;
    }

    /**
     * Method to format the values from the sensors to print them to the socket.
     * @param values Array of length 3 of float variables.
     * @return Values formatted.
     */
    private String valuesString(float[] values) {
        String s = "";
        if(values.length>0){
            for(int i=0;i<=values.length-1;i++){
                s += values[i]+";";
            }
        }
        return s;
    }
}