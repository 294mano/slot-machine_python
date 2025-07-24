from flask import Flask, render_template_string, request, jsonify
import random

app = Flask(__name__)

# 拉霸機符號
SYMBOLS = ['🍎', '🍊', '🍇', '🍒', '🔔', '💎', '7️⃣']
SYMBOL_WEIGHTS = [30, 25, 20, 15, 5, 3, 2]  # 出現機率權重

# HTML模板
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>拉霸機遊戲</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        h1 {
            color: #333;
            margin-bottom: 30px;
        }
        .slot-machine {
            display: flex;
            justify-content: center;
            margin: 30px 0;
            gap: 10px;
        }
        .reel {
            width: 100px;
            height: 100px;
            border: 3px solid #333;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 50px;
            background: #f9f9f9;
            box-shadow: inset 0 2px 5px rgba(0,0,0,0.1);
        }
        .spinning {
            animation: spin 0.5s ease-in-out;
        }
        @keyframes spin {
            0% { transform: rotateY(0deg); }
            50% { transform: rotateY(180deg); }
            100% { transform: rotateY(360deg); }
        }
        button {
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 18px;
            border-radius: 50px;
            cursor: pointer;
            margin: 10px;
            transition: transform 0.2s;
        }
        button:hover {
            transform: scale(1.05);
        }
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .info {
            margin: 20px 0;
            font-size: 18px;
        }
        .credits {
            color: #27ae60;
            font-weight: bold;
        }
        .result {
            margin: 20px 0;
            font-size: 20px;
            font-weight: bold;
            min-height: 30px;
        }
        .win {
            color: #27ae60;
            animation: glow 1s ease-in-out;
        }
        .lose {
            color: #e74c3c;
        }
        @keyframes glow {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎰 拉霸機遊戲 🎰</h1>
        
        <div class="info">
            <div class="credits">點數: <span id="credits">{{ credits }}</span></div>
        </div>
        
        <div class="slot-machine">
            <div class="reel" id="reel1">🍎</div>
            <div class="reel" id="reel2">🍊</div>
            <div class="reel" id="reel3">🍇</div>
        </div>
        
        <div class="result" id="result"></div>
        
        <button id="spinBtn" onclick="spin()">開始轉動 (花費: 10點)</button>
        <button onclick="resetGame()">重新開始</button>
        
        <div style="margin-top: 30px; font-size: 14px; color: #666;">
            <h3>獎勵規則:</h3>
            <p>三個相同: +100點 | 兩個相同: +20點 | 7️⃣7️⃣7️⃣: +500點 | 💎💎💎: +1000點</p>
        </div>
    </div>

    <script>
        let spinning = false;
        
        function spin() {
            if (spinning) return;
            
            const credits = parseInt(document.getElementById('credits').textContent);
            if (credits < 10) {
                document.getElementById('result').innerHTML = '<span class="lose">點數不足！</span>';
                return;
            }
            
            spinning = true;
            document.getElementById('spinBtn').disabled = true;
            document.getElementById('result').textContent = '';
            
            // 添加旋轉動畫
            document.querySelectorAll('.reel').forEach(reel => {
                reel.classList.add('spinning');
            });
            
            fetch('/spin', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                setTimeout(() => {
                    document.getElementById('reel1').textContent = data.symbols[0];
                    document.getElementById('reel2').textContent = data.symbols[1];
                    document.getElementById('reel3').textContent = data.symbols[2];
                    document.getElementById('credits').textContent = data.credits;
                    
                    const resultElement = document.getElementById('result');
                    if (data.win_amount > 0) {
                        resultElement.innerHTML = `<span class="win">恭喜中獎！獲得 ${data.win_amount} 點！</span>`;
                    } else {
                        resultElement.innerHTML = '<span class="lose">沒有中獎，再試一次！</span>';
                    }
                    
                    document.querySelectorAll('.reel').forEach(reel => {
                        reel.classList.remove('spinning');
                    });
                    
                    spinning = false;
                    document.getElementById('spinBtn').disabled = false;
                }, 1000);
            });
        }
        
        function resetGame() {
            fetch('/reset', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('credits').textContent = data.credits;
                document.getElementById('result').textContent = '';
                document.getElementById('reel1').textContent = '🍎';
                document.getElementById('reel2').textContent = '🍊';
                document.getElementById('reel3').textContent = '🍇';
            });
        }
        
        // 允許按Enter鍵轉動
        document.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                spin();
            }
        });
    </script>
</body>
</html>
'''

class SlotMachine:
    def __init__(self):
        self.credits = 100
        self.bet_amount = 10
    
    def spin(self):
        if self.credits < self.bet_amount:
            return None, 0, self.credits
        
        # 扣除下注金額
        self.credits -= self.bet_amount
        
        # 隨機產生三個符號
        symbols = random.choices(SYMBOLS, weights=SYMBOL_WEIGHTS, k=3)
        
        # 計算獲勝金額
        win_amount = self.calculate_win(symbols)
        self.credits += win_amount
        
        return symbols, win_amount, self.credits
    
    def calculate_win(self, symbols):
        # 特殊組合
        if symbols == ['💎', '💎', '💎']:
            return 1000  # 鑽石三連
        elif symbols == ['7️⃣', '7️⃣', '7️⃣']:
            return 500   # 777大獎
        
        # 三個相同
        if symbols[0] == symbols[1] == symbols[2]:
            return 100
        
        # 兩個相同
        if (symbols[0] == symbols[1] or 
            symbols[1] == symbols[2] or 
            symbols[0] == symbols[2]):
            return 20
        
        return 0
    
    def reset(self):
        self.credits = 100

# 全域遊戲實例
game = SlotMachine()

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, credits=game.credits)

@app.route('/spin', methods=['POST'])
def spin():
    symbols, win_amount, credits = game.spin()
    if symbols is None:
        return jsonify({
            'error': '點數不足',
            'credits': credits
        })
    
    return jsonify({
        'symbols': symbols,
        'win_amount': win_amount,
        'credits': credits
    })

@app.route('/reset', methods=['POST'])
def reset():
    game.reset()
    return jsonify({'credits': game.credits})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
