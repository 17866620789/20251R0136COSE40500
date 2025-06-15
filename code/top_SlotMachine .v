module top_SlotMachine(
   input CLOCK_50,   // 50MHz -> 1sec per 5000000 clock cycle
   input [1:0] KEY,   
   output [0:6] HEX0, HEX1, HEX2
);
// KEY[1]: Stop all values
// KEY[0]: reset

localparam IDLE = 0,
            GAME = 1,
            REPORT = 2;

localparam HEX0_delay = 'd50000000,
           HEX1_delay = 'd8000000,
           HEX2_delay = 'd15000000;

reg [3:0] val[0:2];          // 7-segment value in the GAME state
reg [3:0] _7seg[0:2];        // 7-segment displaying value
reg [31:0] cnt_reg[0:2];      // counter register
reg [31:0] cmp_reg[0:2];      // compare register
reg [1:0] state = 0;

wire clk, rst, next;
assign clk = CLOCK_50;
assign rst = KEY[0];
assign next = KEY[1];

// Displaying 7-segment value
digit_to_hex hex0(_7seg[0], HEX0);           
digit_to_hex hex1(_7seg[1], HEX1);
digit_to_hex hex2(_7seg[2], HEX2);

// Compare register setting
always @(*) begin
      cmp_reg[0] = HEX0_delay;
      cmp_reg[1] = HEX1_delay;
      cmp_reg[2] = HEX2_delay;
end

// Clock
always @(posedge clk or negedge rst) begin
   if (!rst) begin
      cnt_reg[0] <= 0;
      val[0] <= 0;
   end
   else if (next) begin
      // Stop
      cnt_reg[0] <= cnt_reg[0];
      val[0] <= val[0];
   end
   else if (cnt_reg[0] == cmp_reg[0]) begin
      // Increase 7-segment value
      cnt_reg[0] <= 0;
      if (val[0] == 9) begin
         val[0] <= 0;
      end
      else begin
         val[0] <= val[0] + 1;
      end
   end
   else begin
      // Increase counter register
      cnt_reg[0] <= cnt_reg[0] + 1;
      val[0] <= val[0];
   end
end

// Repeat the clock block for cnt_reg[1] and cnt_reg[2]

// Additional variables for game logic
reg [3:0] game_score = 0; 
reg [1:0] stop_counter = 0;

// Game and State Logic
always @(posedge clk or negedge rst) begin
    if (!rst) begin
        game_score <= 0;
        stop_counter <= 0;
        _7seg[0] <= 0;
        _7seg[1] <= 0;
        _7seg[2] <= 0;
        state <= IDLE;
    end
    else begin
        case (state)
            GAME: begin
                if (!next) begin
                    stop_counter <= stop_counter + 1;
                    _7seg[0] <= val[0];
                    _7seg[1] <= val[1]; 
                    _7seg[2] <= val[2];

                    // Calculate score
                    if (val[0] == 7) game_score <= game_score + 1;
                    if (val[1] == 7) game_score <= game_score + 1;
                    if (val[2] == 7) game_score <= game_score + 1;

                    // Check if it's time to stop
                    if (stop_counter == 3) begin
                        state <= REPORT; 
                        stop_counter <= 0; 
                    end
                end
            end
            REPORT: begin
                // Display game score
                _7seg[0] <= game_score;
                _7seg[1] <= 7'b1111111;
                _7seg[2] <= 7'b1111111;

                // Return to IDLE state
                if (!next) begin
                    state <= IDLE;
                end
            end
            IDLE: begin
               if (!next) begin
                  state <= GAME;
               end
            end
        endcase
    end
end

endmodule

// 7-segment display module
module digit_to_hex(
   input [3:0] digit,
   output reg [0:6] hex
);

parameter Seg9 = 7'b000_1100;
parameter Seg8 = 7'b000_0000;
parameter Seg7 = 7'b000_1111;
parameter Seg6 = 7'b010_0000;
parameter Seg5 = 7'b010_0100;
parameter Seg4 = 7'b100_1100;
parameter Seg3 = 7'b000_0110;
parameter Seg2 = 7'b001_0010;
parameter Seg1 = 7'b100_1111;
parameter Seg0 = 7'b000_0001;

always @(*) begin
   case(digit)
      9: hex = Seg9;    
      8: hex = Seg8;   
      7: hex = Seg7;   
      6: hex = Seg6;
      5: hex = Seg5;   
      4: hex = Seg4;   
      3: hex = Seg3;   
      2: hex = Seg2;
      1: hex = Seg1;
      0: hex = Seg0;  
      default: hex = 7'b1111111;
   endcase
end
endmodule
