#include "C:\Users\Honza\Documents\PIC\hlidani\main.h"
//REL1SW01A - v�echny moduly mus� m�t jupery mezi VCC-pin1 a VCC-pin10

//Zapojen� rel. pro odpojen� ODROID
//PIC - REL   REL - REL
//RA0 - IN1 a OUT1 - pin6
//RA1 - IN2 a OUT2 - pin5

//Nap�jec� nap�t� p�ivedeno na pin3 a v�stup k za��zen� z pin2

#define  ODROID_ON_1    output_high(PIN_A0)  // Makra pro ovladani akcnich clenu
#define  ODROID_OFF_1   output_high(PIN_A1)
#define  ODROID_ON_0    output_low(PIN_A0)  // Makra pro ovladani akcnich clenu
#define  ODROID_OFF_0   output_low(PIN_A1)

#define  IN_ODROID    input(PIN_B0) //kdy� log. 0 rele je seple, log.1 rele odpojeno

 int ODROID_I=0; //kontrolni promena, ktera zamezuje, aby se obvod pokousel st�le prepinat rele do polohy ve kter� ji� je (�et�� energii)

//Zapojen� rel. pro odpojen� PCDR
//PIC - REL   REL - REL
//RA2 - IN1 a OUT1 - pin6
//RA3 - IN2 a OUT2 - pin5

//Nap�jec� nap�t� p�ivedeno na pin3 a v�stup k za��zen� z pin2

#define  PCDR_ON_1    output_high(PIN_A2)  // Makra pro ovladani akcnich clenu
#define  PCDR_OFF_1   output_high(PIN_A3)
#define  PCDR_ON_0    output_low(PIN_A2)  // Makra pro ovladani akcnich clenu
#define  PCDR_OFF_0   output_low(PIN_A3)

#define  IN_PCDR    input(PIN_B1) //kdy� log. 0 rele je seple, log.1 rele odpojeno

 int PCDR_I=0; //kontrolni promena, ktera zamezuje, aby se obvod pokousel st�le prepinat rele do polohy ve kter� ji� je (�et�� energii)

//Zapojen� rel. pro odpojen� GPS
//PIC - REL   REL - REL
//RD4 - IN1 a OUT1 - pin6
//RD5 - IN2 a OUT2 - pin5

//Nap�jec� nap�t� p�ivedeno na pin3 a v�stup k za��zen� z pin2

#define  GPS_ON_1    output_high(PIN_D4)  // Makra pro ovladani akcnich clenu
#define  GPS_OFF_1   output_high(PIN_D5)
#define  GPS_ON_0    output_low(PIN_D4)  // Makra pro ovladani akcnich clenu
#define  GPS_OFF_0   output_low(PIN_D5)

#define  IN_GPS    input(PIN_B2) //kdy� log. 0 rele je seple, log.1 rele odpojeno

 int GPS_I=0; //kontrolni promena, ktera zamezuje, aby se obvod pokousel st�le prepinat rele do polohy ve kter� ji� je (�et�� energii)

//Zapojen� rel. pro odpojen� GPRS
//PIC - REL   REL - REL
//RD6 - IN1 a OUT1 - pin6
//RD7 - IN2 a OUT2 - pin5

//Nap�jec� nap�t� p�ivedeno na pin3 a v�stup k za��zen� z pin2

#define  GPRS_ON_1    output_high(PIN_D6)  // Makra pro ovladani akcnich clenu
#define  GPRS_OFF_1   output_high(PIN_D7)
#define  GPRS_ON_0    output_low(PIN_D6)  // Makra pro ovladani akcnich clenu
#define  GPRS_OFF_0   output_low(PIN_D7)

#define  IN_GPRS    input(PIN_B3) //kdy� log. 0 rele je seple, log.1 rele odpojeno

 int GPRS_I=0; //kontrolni promena, ktera zamezuje, aby se obvod pokousel st�le prepinat rele do polohy ve kter� ji� je (�et�� energii)

 int timer1=0;


#int_TIMER1
void  TIMER1_isr(void) //pokud neni do definovan�ho okamziku vynulovan timer1, tak se resetuje napajeni odroidu
{
   if(timer1>3) //slouz� pro prodlouzeni casu
         {
         ODROID_OFF_1;           // odpoj� rel�
         delay_ms(1000);
         ODROID_OFF_0;
         ODROID_ON_1;           // pripoj� rel�
         delay_ms(10);
         ODROID_ON_0;
         ODROID_I=1;
         set_timer0(0);
         timer1=0;
         }
   else
   {
   timer1=timer1+1;      
   }
 }


#int_TIMER0 //pro preteceni ��ta�e od odroid (RA4), kdyz dava odroid pulzy, tak se vzdy po preteceni vynuluje timer1
void  TIMER0_isr(void) 
{
        set_timer1(0); 
        timer1=0;
}




void main()
{
   port_b_pullups(TRUE);      // Pullupy pro pripojeni tlacitka

   
   setup_adc_ports(NO_ANALOGS);
   setup_adc(ADC_OFF);
   setup_spi(SPI_SS_DISABLED);
   setup_timer_0(RTCC_EXT_L_TO_H|RTCC_DIV_1);
   setup_timer_1(T1_EXTERNAL|T1_DIV_BY_8|T1_CLK_OUT);
   setup_timer_2(T2_DISABLED,0,1);
   setup_comparator(NC_NC_NC_NC);
   setup_vref(FALSE);
   
   
   enable_interrupts(INT_TIMER1);
   enable_interrupts(INT_TIMER0);
   enable_interrupts(GLOBAL);

ODROID_ON_1; //zapnut� nap�jen� odroidu
delay_ms(10);
ODROID_ON_0;
ODROID_I=1;

PCDR_ON_1; //zapnut� nap�jen� PCDR
delay_ms(10);
PCDR_ON_0;
PCDR_I=1;

GPS_ON_1; //zapnut� nap�jen� GPS
delay_ms(10);
GPS_ON_0;
GPS_I=1;

GPRS_ON_1; //zapnut� nap�jen� GPRS
delay_ms(10);
GPRS_ON_0;
GPRS_I=1;
      
   while(TRUE)
   {

//----------------------------------------------------------------------
//----------------------------------------------------------------------
   //osetruje odpojeni napajeni ODROIDU na extern� pokyn
   if(IN_ODROID)
      {
      if(ODROID_I)
         {
         ODROID_OFF_1;           // odpoj� rel�
         delay_ms(10);
         ODROID_OFF_0;
         ODROID_I=0;
         }
         else
         {
         }
       }     
      else
      {
     
       
      if(ODROID_I)
         {
         }
         else
         {
         ODROID_ON_1;           // pripoj� rel�
         delay_ms(10);
         ODROID_ON_0;
         ODROID_I=1;
         }
     
      }
      
      
//----------------------------------------------------------------------
//----------------------------------------------------------------------
   //osetruje odpojeni napajeni PCDR na extern� pokyn
   if(IN_PCDR)
      {
      if(PCDR_I)
         {
         PCDR_OFF_1;           // odpoj� rel�
         delay_ms(10);
         PCDR_OFF_0;
         PCDR_I=0;
         }
         else
         {
         }
       }     
      else
      {
     
       
      if(PCDR_I)
         {
         }
         else
         {
         PCDR_ON_1;           // pripoj� rel�
         delay_ms(10);
         PCDR_ON_0;
         PCDR_I=1;
         }
      
     
      }
      
      
//----------------------------------------------------------------------
//----------------------------------------------------------------------
   //osetruje odpojeni napajeni GPS na extern� pokyn
   if(IN_GPS)
      {
      if(GPS_I)
         {
         GPS_OFF_1;           // odpoj� rel�
         delay_ms(10);
         GPS_OFF_0;
         GPS_I=0;
         }
         else
         {
         }
       }     
      else
      {
     
       
      if(GPS_I)
         {
         }
         else
         {
         GPS_ON_1;           // pripoj� rel�
         delay_ms(10);
         GPS_ON_0;
         GPS_I=1;
         }      
      }
      
 //----------------------------------------------------------------------
//----------------------------------------------------------------------
   //osetruje odpojeni napajeni GPRS na extern� pokyn
   if(IN_GPRS)
      {
      if(GPRS_I)
         {
         GPRS_OFF_1;           // odpoj� rel�
         delay_ms(10);
         GPRS_OFF_0;
         GPRS_I=0;
         }
         else
         {
         }
       }     
      else
      {
     
       
      if(GPRS_I)
         {
         }
         else
         {
         GPRS_ON_1;           // pripoj� rel�
         delay_ms(10);
         GPRS_ON_0;
         GPRS_I=1;
         }           
      }
      
      
      
      
      
     } 
     

} 
     
