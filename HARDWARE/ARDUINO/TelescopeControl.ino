#include <TimerOne.h>

/*************************************************/

/***** Current angle read by the encoder******/
long npasos1=0;
long npasos2=0;
/********dutyCycle given to the PWM pins**********/
unsigned int dutyCycle1=512;
unsigned int dutyCycle2=512;
/********PID of the systems *********************/
long pid1=0;
long pid2=0;
/********* SetPoints **********/

long setPoint=0000;
long setPoint2=60000;
int  setPoint3=555;

/**If this flag the variables PID are updated****/
/**Used to adjust the sample rate****************/
boolean sampleFlag=true;
/********************************************/
String strRecibido = ""; //Serial buffer length = TOTAL_SIZE
String strMotor1="", strMotor2="", strMotor3="";
boolean complete = false;
int cont=0;
byte TOTAL_SIZE = 10; //Total length received by serial
int chrBuffer=0;


void setup(){
  /************************/
  Serial.begin(115200);
  strRecibido.reserve(TOTAL_SIZE);
  
  /************************/
  pinMode(10, OUTPUT);// Enable Motor 1
  pinMode(11, OUTPUT);// Direction Motor 1
  pinMode(12, OUTPUT);// Direction Motor 1
  
  pinMode(9, OUTPUT);// Enable Motor 2
  pinMode(7, OUTPUT);// Direction Motor 2
  pinMode(8, OUTPUT);// Direction Motor 2
  
  pinMode(5, INPUT);// Read Direction encoder 1
  pinMode(6, INPUT);// Read Direction encoder 2

  pinMode(2, INPUT);// Read Pulses encoder 1
  pinMode(3, INPUT);// Read Pulses encoder 2
  
  /*******************************/
  attachInterrupt(0, encoder1, RISING);//Interrupts attached to the pin 2. Encoder 1 
  attachInterrupt(1, encoder2, RISING);//Interrupts attached to the pin 3. Encoder 2
  /*******************************/
  Timer1.initialize(250); // Initialization of Timer 1 for sample rate. 
  Timer1.pwm(10, 512); // Enables PWM on pin 10
  Timer1.pwm(9, 512); // Enables PWM on pin 9
  Timer1.attachInterrupt(Sampling); // Interrupt attached to the timer1
  /*****************************/
  delay(5000);  
  /*****************************/
}


void loop(){
  while(Serial.available()){
    //char chrBuffer = (char) Serial.read();
    int chrBuffer = (int) Serial.read(); //Save as int instead of ASCII char
    if(isDigit(chrBuffer) || chrBuffer=='-' || chrBuffer=='+'){ //Testing whether type is int (necesary to avoid errors)
      strRecibido += (char) chrBuffer; //int to char to save in String variable
    }
    cont += 1;
    if(chrBuffer == '\n'){
      complete = true;
    }
  }
  
  if(complete){
    //concatenando chars
    strMotor1 = (String) strRecibido[0] + strRecibido[1] + strRecibido[2] + strRecibido[3] + strRecibido[4] + strRecibido[5] + strRecibido[6];
    strMotor2 = (String) strRecibido[7] + strRecibido[8] + strRecibido[9] + strRecibido[10] + strRecibido[11] + strRecibido[12] + strRecibido[13];;
    strMotor3 = (String) strRecibido[14] + strRecibido[15] + strRecibido[16]+ strRecibido[17];
    //Mostrando en consola serial
    setPoint=strMotor1.toInt();
    setPoint2=strMotor2.toInt();
    setPoint3=strMotor3.toInt();
    strRecibido = "";
    cont = 0;
    complete = false;
  }
  
   if(sampleFlag==true)
   {      
     pid1=(setPoint-npasos1)*10; //Proportional closed loop for motor 1
     pid2=(setPoint2-npasos2)*8; //Proportional closed loop for motor 2
     
/********Digital implementation of negative numbers on the pid**************/     
/************************Motor1******************************************/
     if(pid1>0){
       dutyCycle1=pid1;
       digitalWrite(11, HIGH);
       digitalWrite(12, LOW);
     }
     else{
       dutyCycle1=-pid1;
       digitalWrite(11, LOW);
       digitalWrite(12, HIGH);
     }
/********Digital implementation of negative numbers on the pid**************/     
/************************Motor2******************************************/

     if(pid2>0){
       dutyCycle2=pid2;
       digitalWrite(8, HIGH);
       digitalWrite(7, LOW);
     }
     else{
       dutyCycle2=-pid2;
       digitalWrite(7, HIGH);
       digitalWrite(8, LOW);
       
     }
/*********************Avoid Overflow in PWM Module********************************/
/******************************************************************/

     if(dutyCycle1>=1024){
       dutyCycle1=1023;
     }
     else if(dutyCycle1<45){
       dutyCycle1=0;
     }
     
     if (dutyCycle2>=1024){
       dutyCycle2=1023;
     }
     else if(dutyCycle2<45){
       dutyCycle2=0;
     }
    /****Updating outputs to the motors******/ 
     
     Timer1.pwm(10, dutyCycle1);
     Timer1.pwm(9, dutyCycle2);
     sampleFlag=false;
   /****************************/
   }
}


void Sampling(){
  digitalWrite(13, digitalRead(13)^1);
  sampleFlag=true;
}

/*Interrupts used to sense Motor 1 dynamics*/
void encoder1(){
  /****Reading the angle given in pulses **/
  if(digitalRead(5)==HIGH){
   npasos1=npasos1+1; 
  }
  else{
   npasos1=npasos1-1;
  }
}

/*Interrupts used to sense Motor 2 dynamics*/
void encoder2(){
  /****Reading the angle given in pulses**/
  if(digitalRead(6)==HIGH){
   npasos2=npasos2+1; 
  }
  else{
   npasos2=npasos2-1;
  } 
}




