/*******************************************************************************
*
*******************************************************************************/
#include <stdio.h>
#include <stdlib.h>

//#include <kos/dbgio.h>
#include <kos.h>
#include <dc/sound/sound.h>
//KOS_INIT_FLAGS(INIT_QUIET);

#include "protocol.h"

//FILE* fin = NULL;
//int fin = 0;
file_t fin = (file_t)-1;

#define NAMEDPIPEFILE "/pc/bin/tmpUIXCHG.bin"

/*******************************************************************************
*
*******************************************************************************/
void closeNamedPipe (void){
 //if (fin) fclose(fin);
 //if (fin) close(fin);
 //if (fin >= 0){
   fs_close(fin);
   printf("Named pipe closed\n");
 //} 
}

/*******************************************************************************
*
*******************************************************************************/
int openNamedPipe (void){
 //char buffer[20];
 //fin = fopen(NAMEDPIPEFILE, "rb");
 //fin = open(NAMEDPIPEFILE, O_RDONLY);

 //TODO: loop if failed - wait 5 seconds before retry
 
 fin = fs_open (NAMEDPIPEFILE, O_RDONLY | O_NONBLOCK );
 //if (!fin) {
 if (fin < 0) {
    printf("ERROR open named pipe: %s\n", NAMEDPIPEFILE);
    return 0;
 } else {
    printf("Opened named pipe: %s\n", NAMEDPIPEFILE);
    //memset ((void*)&buffer, 0x00, 20);
      //fread ((char*)&buffer, 19, 1, fin);
    //fs_read(fin, buffer, 10);
    //printf ("BYTES READ: %s", buffer);
 }
 return 1;
}

/*******************************************************************************
*
*******************************************************************************/
void appShutdown (void){
 closeNamedPipe();

 /* Wait 15 seconds for the user to see what's on the screen before we clear
   it during the exit back to the loader */
 thd_sleep(15 * 1000);//sleep  TODO: needed ?

 snd_shutdown();

 exit(0);
}

/*******************************************************************************
*
*******************************************************************************/
void* checkPadForExit (void *v) {
 maple_device_t *cont;
 cont_state_t *state;

 //check for START button press to exit
 //while (1){
    cont = maple_enum_type(0, MAPLE_FUNC_CONTROLLER);
    state = (cont_state_t *)maple_dev_status(cont);// Check key status

    if (!state) {
        printf("Error reading controller\n");
        appShutdown();
    }

    if (state->buttons & CONT_START){
        printf("START pressed. Exiting...\n");
        appShutdown();
    }
 //}

 return NULL;
}


/*******************************************************************************
*
*******************************************************************************/
int main(int argc, char **argv) {
 //kthread_t* padThread;

 // Set the framebuffer as the output device for dbgio.
 //dbgio_dev_select("fb");

 if (!openNamedPipe()){ 
    thd_sleep(10 * 1000);//sleep TODO: needed ?
    return 1;
 }

 // Initialize sound system
 snd_init();

 // Launch the check for exit on the gamepad in a separate thread, so that fs_read can just be blocking & wait for the next command.
 printf ("Press START to exit...\n");
 //padThread = 
 //thd_create(1, checkPadForExit, NULL);

 while (executeCommands(fin)){ //TODO: fs_read is blocking, so blocks the full DC, so there is little point to having the pad check in a separate thread...
   //thd_sleep(16); //sleep 16 msecs TODO: needed ?
   //checkPadForExit(NULL);
 };
 
 appShutdown();

 return 0;
}