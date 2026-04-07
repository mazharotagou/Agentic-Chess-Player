from fasthtml.common import *
from packages import chess_
from packages.crewai_main import run
import json


app, rt = fast_app(
    hdrs=(
        Link(
            rel="stylesheet",
            href="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.css",
        ),
        Script(src="https://code.jquery.com/jquery-3.6.0.min.js"),
        Script(src="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.js"),
        Script(src="https://cdnjs.cloudflare.com/ajax/libs/chess.js/0.10.3/chess.min.js"),
    )
)

@rt("/")
def home():
    return Title("Agentic Chess Player"), Main(
        H1("Agentic Chess Player"),
        P("White to Play First, by simply dragging and dropping the piece."),
        Div(id="board", style="width: 600px;"),
        Pre(id="status", style="margin-top:20px; padding:10px; background:#f5f5f5;"),
        Script("""
document.addEventListener("DOMContentLoaded", function () {
    const game = new Chess();

    

    function showStatus(msg) {
        document.getElementById("status").textContent = msg;
    }

    function sendStateToBackend(move) {
        const payload = {
            fen: game.fen(),
            pgn: game.pgn(),
            turn: game.turn(),
            from: move.from,
            to: move.to,
            san: move.san
        };

        fetch("/game_state", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        })
        .then(function(r) {
            return r.text();
                })
        .then(function(nextmove) {
            const moveObj = {
                from: nextmove.slice(0, 2),
                to: nextmove.slice(2, 4)
            };

            if (nextmove.length === 5) {
                moveObj.promotion = nextmove[4];
            }

            const appliedMove = game.move(moveObj);

            if (appliedMove === null) {
                showStatus("Backend sent an illegal move: " + nextmove);
                return;
            }

            board.position(game.fen());
            showStatus("Agent move: " + appliedMove.san);
        })
        .catch(err => {
            showStatus("Backend error: " + err);
        });
    }

    function onDragStart(source, piece) {
        if (game.game_over()) return false;

        if (game.turn() === "b") return false;
               
        if (
            (game.turn() === "w" && piece.startsWith("b")) ||
            (game.turn() === "b" && piece.startsWith("w"))
        ) {
            return false;
        }
    }

    function onDrop(source, target) {
        const move = game.move({
            from: source,
            to: target,
            promotion: "q"
        });

        if (move === null) return "snapback";

        board.position(game.fen());
        if (game.turn() === "b") {
            sendStateToBackend(move);
            showStatus("Waiting for agent's move...");
        } else {
            showStatus("Your move: " + move.san);
        }
        
    }

    const board = Chessboard("board", {
        position: "start",
        draggable: true,
        showErrors: "console",
        pieceTheme: "https://chessboardjs.com/img/chesspieces/wikipedia/{piece}.png",
        onDragStart: onDragStart,
        onDrop: onDrop
    });

    showStatus("Ready. Current FEN: " + game.fen());
});
        """)
    )

@rt("/game_state")
async def post(req):
    server_side_color = "Black"
    data = await req.json()
    fen = data.get("fen", "")
    print ("The FEN notation is ", fen)
    pgn = data.get("pgn", "")
    turn = data.get("turn", "")
    from_sq = data.get("from", "")
    to_sq = data.get("to", "")
    san = data.get("san", "")

    if chess_.checkmate_test(fen):
        return Div(
            H2("Checkmate!"),
            P("Congratulations, you won! Refresh to play again.")
        )
    else:
        if turn == "b":
            legal_moves = chess_.legal_moves_black(fen)
            result = run(chess_state=fen, color=server_side_color, legal_moves=legal_moves)
            #result format is result.best_move, result.reason
            return result
            
if __name__ == "__main__":
    serve()
