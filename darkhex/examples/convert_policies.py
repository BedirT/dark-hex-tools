import pyspiel
import darkhex.utils.util as util
import darkhex.policy as darkhexPolicy

data_path = "darkhex/data/policies/4x3_handcrafted_new_polgen_pr/game_info.pkl"
data = util.load_file(data_path)

game = pyspiel.load_game("dark_hex", {
    "num_rows": data["num_rows"],
    "num_cols": data["num_cols"]
})
s = data["strategy"].policy
p = darkhexPolicy.SinglePlayerTabularPolicy(
    s,
    player=data["player"],
    board_size=[data["num_rows"], data["num_cols"]],
    initial_state=game.new_initial_state(),
    is_best_response=False,
    is_perfect_recall=True)
p.save_policy_to_file("4x3_handcrafted_new_polgen_pr")
