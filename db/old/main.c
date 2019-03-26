#include <stdio.h>
#include <unistd.h>

int main() {
		int i;
		for (i = 1; i < 100; i++) {
				printf("%d\r", i);
				fflush(stdout);
				sleep(1);
		}
		printf("\n");

		return 0;
}
