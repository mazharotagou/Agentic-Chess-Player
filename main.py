from fasthtml.common import *

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
    return Title("FastHTML Chess Agent"), Main(
        H1("Agentic Chess Player"),
        P("Move a piece, then send the game state to the backend."),
        Div(id="board", style="width: 400px;"),
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
        .then(r => r.text())
        .then(html => {
            document.getElementById("status").innerHTML = html;
        })
        .catch(err => {
            showStatus("Backend error: " + err);
        });
    }

    function onDragStart(source, piece) {
        if (game.game_over()) return false;

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
        sendStateToBackend(move);
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
    data = await req.json()
    fen = data.get("fen", "")
    print ("The FEN notation is ", fen)
    pgn = data.get("pgn", "")
    turn = data.get("turn", "")
    from_sq = data.get("from", "")
    to_sq = data.get("to", "")
    san = data.get("san", "")

    return Div(
        P(B("Last move: "), f"{from_sq} → {to_sq} ({san})"),
        P(B("Turn: "), "White" if turn == "w" else "Black"),
        P(B("FEN: "), fen),
        P(B("PGN so far: "), pgn if pgn else "No PGN yet")
    )

serve()
