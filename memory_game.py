import tkinter as tk
from tkinter import messagebox, ttk
import random
import time

# ドラクエ風キャラクターの絵柄（32種類）
DRAGON_QUEST_CHARACTERS = [
    '🧙', '🧙‍♂️', '🧙‍♀️', '⚔️', '🛡️', '🏰', '🐉', '👑',
    '🧚', '🧚‍♂️', '🧚‍♀️', '🧝', '🧝‍♂️', '🧝‍♀️', '🧞', '🧞‍♂️',
    '🧟', '🧟‍♂️', '🧟‍♀️', '🧌', '👹', '👺', '🤴', '👸',
    '🤵', '🤵‍♂️', '🤵‍♀️', '👮', '👮‍♂️', '👮‍♀️', '🕵️', '🕵️‍♂️'
]

class MemoryGame:
    def __init__(self, root):
        self.root = root
        self.root.title("神経衰弱 - ドラクエ風")
        
        # ゲーム設定
        self.BOARD_SIZE = 8
        self.TOTAL_CARDS = self.BOARD_SIZE * self.BOARD_SIZE  # 64枚
        self.PAIRS = self.TOTAL_CARDS // 2  # 32ペア
        
        # ゲーム状態
        self.cards = []
        self.buttons = []
        self.revealed = set()  # めくられたカードのインデックス
        self.matched = set()  # 揃ったカードのインデックス
        self.first_click = None
        self.player_score = 0
        self.cpu_score = 0
        self.current_turn = "player"  # "player" or "cpu"
        self.cpu_difficulty = None
        self.game_over = False
        
        # 難易度選択画面を表示
        self.show_difficulty_selection()
    
    def get_card_color(self, char):
        """キャラクターに応じた背景色を返す"""
        color_map = {
            '🧙': '#E6E6FA',  # ラベンダー（魔法使い）
            '🧙‍♂️': '#9370DB',  # ミディアムパープル
            '🧙‍♀️': '#BA55D3',  # ミディアムオーキッド
            '⚔️': '#C0C0C0',  # シルバー（武器）
            '🛡️': '#4169E1',  # ロイヤルブルー（盾）
            '🏰': '#8B4513',  # サドルブラウン（城）
            '🐉': '#FF6347',  # トマト（ドラゴン）
            '👑': '#FFD700',  # ゴールド（王冠）
            '🧚': '#98FB98',  # ペールグリーン（妖精）
            '🧚‍♂️': '#90EE90',  # ライトグリーン
            '🧚‍♀️': '#ADFF2F',  # グリーンイエロー
            '🧝': '#F0E68C',  # カーキ（エルフ）
            '🧝‍♂️': '#DAA520',  # ゴールデンロッド
            '🧝‍♀️': '#FFE4B5',  # モカシン
            '🧞': '#FFA500',  # オレンジ（ジーニー）
            '🧞‍♂️': '#FF8C00',  # ダークオレンジ
            '🧟': '#808080',  # グレー（ゾンビ）
            '🧟‍♂️': '#696969',  # ディムグレー
            '🧟‍♀️': '#778899',  # ライトスレートグレー
            '🧌': '#2F4F4F',  # ダークスレートグレー（トロール）
            '👹': '#DC143C',  # クリムゾン（鬼）
            '👺': '#FF1493',  # ディープピンク
            '🤴': '#0000CD',  # ミディアムブルー（王子）
            '👸': '#FF69B4',  # ホットピンク（王女）
            '🤵': '#000000',  # ブラック（タキシード）
            '🤵‍♂️': '#191970',  # ミッドナイトブルー
            '🤵‍♀️': '#4B0082',  # インディゴ
            '👮': '#000080',  # ネイビー（警察）
            '👮‍♂️': '#1E90FF',  # ドジャーブルー
            '👮‍♀️': '#00BFFF',  # ディープスカイブルー
            '🕵️': '#2F2F2F',  # ダークグレー（探偵）
            '🕵️‍♂️': '#1C1C1C',  # ほぼ黒
            '🕵️‍♀️': '#363636',  # ダークグレー
        }
        return color_map.get(char, '#F5F5F5')  # デフォルトはライトグレー
    
    def show_difficulty_selection(self):
        """難易度選択画面"""
        self.selection_frame = tk.Frame(self.root)
        self.selection_frame.pack(expand=True)
        
        tk.Label(self.selection_frame, text="CPUの強さを選択してください", 
                font=("Arial", 16)).pack(pady=20)
        
        tk.Button(self.selection_frame, text="弱い（ランダム）", 
                 command=lambda: self.start_game("easy"),
                 width=20, height=2, font=("Arial", 12)).pack(pady=10)
        
        tk.Button(self.selection_frame, text="普通（少し記憶）", 
                 command=lambda: self.start_game("medium"),
                 width=20, height=2, font=("Arial", 12)).pack(pady=10)
        
        tk.Button(self.selection_frame, text="強い（完璧な記憶）", 
                 command=lambda: self.start_game("hard"),
                 width=20, height=2, font=("Arial", 12)).pack(pady=10)
    
    def start_game(self, difficulty):
        """ゲーム開始"""
        self.cpu_difficulty = difficulty
        self.selection_frame.destroy()
        
        # カードの準備
        characters = DRAGON_QUEST_CHARACTERS[:self.PAIRS]
        self.cards = (characters + characters).copy()
        random.shuffle(self.cards)
        
        # CPUの記憶（難易度に応じて）
        self.cpu_memory = {}  # {index: character}
        
        # UIの作成
        self.create_ui()
        
        # プレイヤーのターンから開始
        self.update_status()
    
    def create_ui(self):
        """UIの作成"""
        # スコア表示フレーム
        score_frame = tk.Frame(self.root)
        score_frame.pack(pady=10)
        
        self.player_label = tk.Label(score_frame, text=f"プレイヤー: {self.player_score}ペア", 
                                     font=("Arial", 14), fg="blue")
        self.player_label.pack(side=tk.LEFT, padx=20)
        
        self.turn_label = tk.Label(score_frame, text="", font=("Arial", 14, "bold"))
        self.turn_label.pack(side=tk.LEFT, padx=20)
        
        self.cpu_label = tk.Label(score_frame, text=f"CPU: {self.cpu_score}ペア", 
                                  font=("Arial", 14), fg="red")
        self.cpu_label.pack(side=tk.LEFT, padx=20)
        
        # カードボードフレーム（スクロール可能）
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(canvas_frame, width=600, height=600)
        scrollbar_y = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollbar_x = tk.Scrollbar(canvas_frame, orient="horizontal", command=canvas.xview)
        
        self.board_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=self.board_frame, anchor="nw")
        
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # ボタンの作成
        for i in range(self.TOTAL_CARDS):
            btn = tk.Button(self.board_frame, text="?", width=4, height=2,
                           font=("Arial", 12),
                           bg="lightgray", fg="black",
                           command=lambda idx=i: self.card_clicked(idx))
            row = i // self.BOARD_SIZE
            col = i % self.BOARD_SIZE
            btn.grid(row=row, column=col, padx=2, pady=2)
            self.buttons.append(btn)
        
        # スクロール領域の更新
        self.board_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        
        # ウィンドウサイズの設定
        self.root.geometry("700x700")
    
    def update_status(self):
        """ステータス表示の更新"""
        self.player_label.config(text=f"プレイヤー: {self.player_score}ペア")
        self.cpu_label.config(text=f"CPU: {self.cpu_score}ペア")
        
        if self.current_turn == "player":
            self.turn_label.config(text="あなたのターン", fg="blue")
        else:
            self.turn_label.config(text="CPUのターン", fg="red")
    
    def card_clicked(self, index):
        """カードがクリックされたときの処理"""
        if self.game_over or self.current_turn != "player":
            return
        
        if index in self.matched or index in self.revealed:
            return
        
        self.reveal_card(index)
        
        if self.first_click is None:
            self.first_click = index
        else:
            # 2枚目をめくった
            first_idx = self.first_click
            second_idx = index
            self.first_click = None
            # 値をローカル変数に保存してから呼び出す（クロージャの問題を回避）
            self.root.after(1000, lambda f=first_idx, s=second_idx: self.check_match(f, s))
    
    def reveal_card(self, index):
        """カードをめくる"""
        if index in self.matched:
            return
        
        self.revealed.add(index)
        # カラー付きでカードを表示
        char = self.cards[index]
        # 絵文字に応じた背景色を設定
        bg_color = self.get_card_color(char)
        self.buttons[index].config(text=char, state=tk.DISABLED, 
                                  bg=bg_color, fg="black", font=("Arial", 16, "bold"))
    
    def hide_card(self, index):
        """カードを裏に戻す"""
        if index in self.matched:
            return
        
        self.revealed.discard(index)
        self.buttons[index].config(text="?", state=tk.NORMAL, 
                                  bg="lightgray", fg="black", font=("Arial", 12))
    
    def check_match(self, index1, index2):
        """カードの一致を確認"""
        if self.cards[index1] == self.cards[index2]:
            # 一致した
            self.matched.add(index1)
            self.matched.add(index2)
            self.revealed.discard(index1)
            self.revealed.discard(index2)
            
            # スコア更新
            if self.current_turn == "player":
                self.player_score += 1
            else:
                self.cpu_score += 1
            
            # カードを無効化（揃ったことを示す）
            char1 = self.cards[index1]
            char2 = self.cards[index2]
            bg_color1 = self.get_card_color(char1)
            bg_color2 = self.get_card_color(char2)
            self.buttons[index1].config(state=tk.DISABLED, bg=bg_color1, 
                                       fg="black", font=("Arial", 16, "bold"))
            self.buttons[index2].config(state=tk.DISABLED, bg=bg_color2, 
                                       fg="black", font=("Arial", 16, "bold"))
            
            self.update_status()
            
            # ゲーム終了チェック
            if len(self.matched) == self.TOTAL_CARDS:
                self.end_game()
            else:
                # 続けてターン継続
                if self.current_turn == "player":
                    self.update_status()
                    # プレイヤーのターン継続のため、revealedをクリア
                    self.revealed.clear()
                else:
                    # CPUのターン継続
                    self.revealed.clear()
                    self.root.after(500, self.cpu_turn)
        else:
            # 不一致
            self.hide_card(index1)
            self.hide_card(index2)
            
            # CPUの記憶を更新（プレイヤーがめくったカードも記憶）
            if self.current_turn == "player":
                # プレイヤーがめくったカードをCPUの記憶に追加
                self.cpu_memory[index1] = self.cards[index1]
                self.cpu_memory[index2] = self.cards[index2]
            
            # ターン交代
            if self.current_turn == "player":
                self.current_turn = "cpu"
                self.revealed.clear()  # revealedをクリア
                self.update_status()
                self.root.after(1000, self.cpu_turn)  # 少し待ってからCPUのターン
            else:
                self.current_turn = "player"
                self.revealed.clear()  # revealedをクリア
                self.update_status()
    
    def cpu_turn(self):
        """CPUのターン"""
        if self.game_over:
            return
        
        if self.current_turn != "cpu":
            return
        
        if len(self.matched) == self.TOTAL_CARDS:
            self.end_game()
            return
        
        # CPUの難易度に応じた選択
        first_index, second_index = self.cpu_choose_cards()
        
        if first_index is None or second_index is None:
            # 選べない場合はランダム
            available = [i for i in range(self.TOTAL_CARDS) 
                        if i not in self.matched and i not in self.revealed]
            if len(available) < 2:
                self.end_game()
                return
            first_index, second_index = random.sample(available, 2)
        
        # 1枚目をめくる
        self.reveal_card(first_index)
        self.root.update()
        
        # CPUの記憶を更新
        if first_index not in self.cpu_memory:
            self.cpu_memory[first_index] = self.cards[first_index]
        
        # 少し待ってから2枚目をめくる
        delay = 1000 if self.cpu_difficulty == "easy" else 800
        self.root.after(delay, lambda f=first_index, s=second_index: self.cpu_reveal_second(f, s))
    
    def cpu_reveal_second(self, first_index, second_index):
        """CPUが2枚目をめくる"""
        self.reveal_card(second_index)
        self.root.update()
        
        # CPUの記憶を更新
        if second_index not in self.cpu_memory:
            self.cpu_memory[second_index] = self.cards[second_index]
        
        # 一致確認
        self.root.after(1000, lambda f=first_index, s=second_index: self.check_match(f, s))
    
    def cpu_choose_cards(self):
        """CPUがカードを選択"""
        available = [i for i in range(self.TOTAL_CARDS) 
                    if i not in self.matched and i not in self.revealed]
        
        if len(available) < 2:
            return None, None
        
        if self.cpu_difficulty == "easy":
            # 弱い：完全ランダム
            return random.sample(available, 2)
        
        elif self.cpu_difficulty == "medium":
            # 普通：記憶しているカードがあれば使う、なければランダム
            # 記憶から一致するペアを探す
            for idx1 in available:
                if idx1 in self.cpu_memory:
                    char = self.cpu_memory[idx1]
                    for idx2 in available:
                        if idx2 != idx1 and idx2 in self.cpu_memory:
                            if self.cpu_memory[idx2] == char:
                                return idx1, idx2
            
            # 記憶にない場合は、1枚目をランダム、2枚目もランダム
            return random.sample(available, 2)
        
        else:  # hard
            # 強い：完璧な記憶と推論
            # まず、記憶から一致するペアを探す
            for idx1 in available:
                if idx1 in self.cpu_memory:
                    char = self.cpu_memory[idx1]
                    for idx2 in available:
                        if idx2 != idx1 and idx2 in self.cpu_memory:
                            if self.cpu_memory[idx2] == char:
                                return idx1, idx2
            
            # 記憶にないカードを1枚選んで、そのペアを探す
            # 既にめくられたカードのペアを探す
            for idx1 in available:
                char = self.cards[idx1]
                # 同じ文字のカードを探す（既に記憶にあるか、まだめくられていないか）
                for idx2 in available:
                    if idx2 != idx1:
                        if idx2 in self.cpu_memory:
                            if self.cpu_memory[idx2] == char:
                                return idx1, idx2
                        elif self.cards[idx2] == char:
                            # まだ記憶にないが、同じ文字の可能性が高い
                            return idx1, idx2
            
            # それでも見つからない場合は、ランダムに1枚選んでそのペアを探す
            if available:
                first = random.choice(available)
                char = self.cards[first]
                for idx2 in available:
                    if idx2 != first and self.cards[idx2] == char:
                        return first, idx2
                
                # 見つからない場合はランダム
                second = random.choice([a for a in available if a != first])
                return first, second
            
            return random.sample(available, 2)
    
    def end_game(self):
        """ゲーム終了"""
        self.game_over = True
        
        # すべてのボタンを無効化
        for btn in self.buttons:
            btn.config(state=tk.DISABLED)
        
        # 結果表示
        if self.player_score > self.cpu_score:
            result = "あなたの勝利！"
        elif self.cpu_score > self.player_score:
            result = "CPUの勝利！"
        else:
            result = "引き分け！"
        
        message = f"ゲーム終了！\n\n"
        message += f"プレイヤー: {self.player_score}ペア\n"
        message += f"CPU: {self.cpu_score}ペア\n\n"
        message += result
        
        messagebox.showinfo("ゲーム終了", message)
        
        # 再プレイの確認
        if messagebox.askyesno("再プレイ", "もう一度プレイしますか？"):
            self.root.destroy()
            root = tk.Tk()
            game = MemoryGame(root)
            root.mainloop()
        else:
            self.root.destroy()

def main():
    root = tk.Tk()
    game = MemoryGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()
