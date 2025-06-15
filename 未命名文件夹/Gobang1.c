#include <stdio.h>
#define SIZE 19 // 定义棋盘大小

// 函数声明
void printBoard(char board[SIZE][SIZE]);
void makeMove(char board[SIZE][SIZE], int player);

int main() {
    char board[SIZE][SIZE];
    int currentPlayer = 0; // 0代表玩家1, 1代表玩家2

    // 初始化棋盘
    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            board[i][j] = '.';
        }
    }

    // 游戏主循环
    while (1) {
        printBoard(board);
        makeMove(board, currentPlayer);
        currentPlayer = !currentPlayer; // 切换玩家
    }

    return 0;
}

// 打印棋盘
void printBoard(char board[SIZE][SIZE]) {
    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            printf("%c ", board[i][j]);
        }
        printf("\n");
    }
}

// 玩家下棋
void makeMove(char board[SIZE][SIZE], int player) {
    int x, y;
    char playerChar = (player == 0) ? 'X' : 'O';

    printf("玩家 %d 的回合. 输入位置 x y: ", player + 1);
    scanf("%d %d", &x, &y);

    if (x >= 0 && x < SIZE && y >= 0 && y < SIZE && board[x][y] == '.') {
        board[x][y] = playerChar;
    } else {
        printf("无效的移动!\n");
        makeMove(board, player); // 重新下棋
    }
}
