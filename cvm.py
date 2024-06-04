from manim import *
from manim import config as mn_config
import random
import string
from typing import Optional, List

mn_config.media_width = "75%"
mn_config.verbosity = "WARNING"


MEMORY_SIZE = 5
COIN_COLOR = YELLOW_E
SMALL_P_SCALE_FACTOR = .75

SEQ_Z_INDEX = 1
RECAP_Z_INDEX = 5

# constants for the sequence
SEQ_ELS_WIDTH = .75
SEQ_ELS_SPACING = .05
SEQ_COIN_RADIUS = SEQ_ELS_WIDTH / 2 * .75
SEQ_COIN_TEMPLATE = (
    Circle(radius=SEQ_COIN_RADIUS, color=COIN_COLOR, fill_opacity=1)
    .set_stroke(color=BLACK, width=1)
)
# constants for the memory
MEM_ELS_WIDTH = 1.15
MEM_ELS_SPACING = MEM_ELS_WIDTH * 1.15
MEM_COIN_RADIUS = SEQ_COIN_RADIUS
MEM_COIN_TEMPLATE = (
    Circle(radius=MEM_COIN_RADIUS, color=COIN_COLOR, fill_opacity=1)
    .set_stroke(color=BLACK, width=1)
)


SEQ_LEN = 100
random.seed(SEQ_LEN)
while True:
    SEQ = ''.join([random.choice(string.ascii_uppercase) for _ in range(SEQ_LEN)])
    if len(set(SEQ)) == len(set(string.ascii_uppercase)):
        break

print(SEQ)
print(len(set(SEQ)))

class RegularCoinSequenceTosser:

    def __init__(self, k) -> None:
        self.k = k
        self._mod = 2**k
        self._index = 0
        self._g_index = 0

    def toss(self):
        if self.k == 0:
            return 1

        self._index += 1
        self._g_index = (self._index - 1) // self.k
        
        if (self._g_index + 1) % self._mod == 0:
            return 1
        
        is_last_el = (self._index % self.k) == 0
        if is_last_el:
            return 0
        
        return random.choice([0,1])


def build_sequence(self: Scene, n_els=SEQ_LEN):
    seq_els_groups: List[VGroup] = []
    seq_letters: List[Text] = []

    for ith_seq_el, seq_el_str in enumerate(SEQ[:n_els]):
        
        # draw a box
        a_seq_el_box = (
            Square(side_length=SEQ_ELS_WIDTH)
            .set_stroke(width=1)
        )

        # draw the letter inside
        a_seq_letter = (
            Text(seq_el_str, font_size=17)
            .move_to(a_seq_el_box.get_center())
        )
        
        # draw the index above
        a_seq_ix = (
            Text(str(ith_seq_el), font_size=10)
            .next_to(a_seq_el_box, UP, buff=.2)
        )

        # create the group (box + letter + index)
        a_seq_el_group = VGroup(a_seq_el_box, a_seq_letter, a_seq_ix)
        
        # add the group to the scene
        self.add(a_seq_el_box, a_seq_letter, a_seq_ix)

        # keep track of the elements
        seq_letters.append(a_seq_letter)
        seq_els_groups.append(a_seq_el_group)

    # place the sequence in the upperleft corner
    seq_group = (
        VGroup(*seq_els_groups)
        .arrange(buff=SEQ_ELS_SPACING)
        .align_to(self.camera.frame_center, LEFT)
        .shift(1.85*UP + ORIGIN)
        .shift(RIGHT * (SEQ_ELS_WIDTH + SEQ_ELS_SPACING))
    )

    s = (
        Square(side_length=SEQ_ELS_WIDTH * 1.1)
        .set_stroke(color=RED_C, width=5)
        .move_to(seq_els_groups[0][0].get_center())
        .shift(LEFT * (SEQ_ELS_WIDTH + SEQ_ELS_SPACING))
    )
    return seq_group, s

def get_ith_round_formula(i):
    f = MathTex(r'k = ', f'{i}')
    f.set_z_index(RECAP_Z_INDEX)
    f[-1].set_color(LIGHT_PINK).set_stroke(width=2)
    return f

def get_p_formula(ith_round):
    f = MathTex(
        r'p =', 
        (r'1/' + f'{2**ith_round}') if ith_round != 0 else r'1', 
        r' = \left( \frac{1}{2} \right)^{', 
        f'{ith_round}', 
        r'} = ',
        r'P\left(',
        r'\frac{' + str(ith_round) + r'H}{',
        str(ith_round),
        r'\text{ tosses}',
        r'}\right)'
    )
    f.set_z_index(RECAP_Z_INDEX)
    f[1].set_stroke(width=2).set_color(BLUE)
    if ith_round != 0:
        f[1][2:].next_to(f[1][0], RIGHT, buff=0)
        f[1][:2].scale(.5).shift(UL*.15)
    f[2:].set_color(GREY)
    f[3].set_stroke(width=1).set_color(LIGHT_PINK)
    f[6][:-2].set_stroke(width=1).set_color(LIGHT_PINK)
    f[6][-2].set_stroke(width=1).set_color(GREEN)
    f[7].set_stroke(width=1).set_color(LIGHT_PINK)
    f[2:].scale(.5).next_to(f[:2], RIGHT)
    return f

def get_chi_size_formula(s):
    f = MathTex(r'|X|', '=', f'{s}')
    f.set_z_index(RECAP_Z_INDEX)
    f[-1].set_stroke(width=2).set_color(YELLOW)
    return f

def get_chi_over_p_formula(s, ith_round):
    f = MathTex(
        r'\frac{|X|}{p}', 
        '=', 
        r'\frac{' + str(s) + r'}{' + (
            (r'1/' if ith_round != 0 else '') + f'{2**ith_round}' + r'}'
        ),
        r'=', 
        f'{s * 2**ith_round}'
    )
    f.set_z_index(RECAP_Z_INDEX)
    num = f[-3][0]
    num.set_stroke(width=2).set_color(YELLOW)
    den = f[-3][2:]
    den.set_stroke(width=2).set_color(BLUE)
    if ith_round != 0:
        den[2:].next_to(f[-3][2], RIGHT, buff=0)
        den[:2].scale(.5).shift(UL*.15)
        den.set_x(num.get_x())
    return f

def build_recap_els(ith_round, n_mem_els):

    recap_ith_round = get_ith_round_formula(ith_round)
    recap_p = get_p_formula(ith_round)
    recap_chi_size = get_chi_size_formula(n_mem_els)
    recap_chi_over_p = get_chi_over_p_formula(n_mem_els, ith_round)

    return (
        recap_ith_round,
        recap_p,
        recap_chi_size,
        recap_chi_over_p,
    )
        

def cvm_algorithm(self: Scene, only_setup=False, n_els=15, first_els=10, seed=0):

    random.seed(seed)
    
    p = 1
    ith_round = 0

    # random events generators
    k_coin_tosser = RegularCoinSequenceTosser(k=ith_round)
    one_coin_pgen = RegularCoinSequenceTosser(k=1)

    ## TITLE
    title = (
        Tex(r"\underline{\textbf{CVM Algorithm}}")
        .to_edge(UL)
    )
    title.set_z_index(RECAP_Z_INDEX)
    self.add(title)

    ## DRAW THE MEMORY ######################################################### DRAW THE MEMORY
    mem_list: List[Optional[str]] = [None for _ in range(MEMORY_SIZE)]
    mem_els_letters: List[Optional[Text]] = [None for _ in range(MEMORY_SIZE)]
    mem_els_ps: List[Optional[Text]] = [None for _ in range(MEMORY_SIZE)]

    mem_els_groups: List[VGroup] = []
    mem_els_boxes: List[Square] = []
    mem_els_pboxes: List[Rectangle] = []

    for ith_mem_el in range(MEMORY_SIZE):
        # create the square for the letter
        a_mem_el_box = (
            Square(side_length=MEM_ELS_WIDTH)
            .set_stroke(width=2)
        )

        # create the rectangle for the probability
        a_mem_el_pbox = (
            Rectangle(width=MEM_ELS_WIDTH, height=MEM_ELS_WIDTH/2)
            .set_stroke(width=1, color=GREY)
            .next_to(a_mem_el_box, DOWN, buff=.05)
        )

        # create a group for the single memory element (square + rectangle)
        a_mem_el_group = VGroup(a_mem_el_box, a_mem_el_pbox)

        # keep track of these elements
        mem_els_boxes.append(a_mem_el_box)
        mem_els_pboxes.append(a_mem_el_pbox)
        mem_els_groups.append(a_mem_el_group)
    
    # Create a VGroup from the list of elements
    mem_group = (
        VGroup(*mem_els_groups)
        .arrange(buff=0.01)
        .move_to(ORIGIN + DOWN * 1.5)
        .to_edge(RIGHT, buff=1.25)
    )
    chi_text = (
        MathTex(r'X')
        .next_to(mem_els_boxes[0], LEFT, aligned_edge=RIGHT, buff=.75)
    )
    pchi_text = (
        MathTex('p_{\chi}')
        .scale(.5)
        .next_to(mem_els_pboxes[0], LEFT, aligned_edge=RIGHT, buff=.75)
    )
    mem_group.add(chi_text, pchi_text)

    _hidden_pruning_coin = (
        MEM_COIN_TEMPLATE.copy()
        .next_to(mem_els_groups[-1], DOWN, buff=.3)
    )
    mem_group.add(_hidden_pruning_coin.copy().set_opacity(0))

    mem_surr_rect = SurroundingRectangle(
        mem_group,
        color=GREY,
        buff=MED_SMALL_BUFF
    ).set_stroke(width=1, opacity=.7)

    mem_title = (
        Tex('Memory', font_size=25)
        .next_to(mem_surr_rect, UP, aligned_edge=UL)
    )

    self.add(
        mem_group, 
        mem_surr_rect,
        mem_title,
    )

    ## DRAW THE SEQUENCE ####################################################### DRAW THE SEQUENCE
    seq_group, selection_square = build_sequence(self, n_els=n_els)
    seq_group.set_z_index(SEQ_Z_INDEX)

    _size = 3.5
    _seq_surr_rect_g = Group(
        selection_square.copy().shift(LEFT * (SEQ_ELS_SPACING + SEQ_ELS_WIDTH) * .6).set_opacity(0),
        selection_square.copy().shift(RIGHT * (SEQ_ELS_SPACING + SEQ_ELS_WIDTH) * 6.35).set_opacity(0),
        seq_group[0][-1].copy().set_opacity(0),
        SEQ_COIN_TEMPLATE.copy().next_to(selection_square, DOWN).set_opacity(0),
    )
    seq_surr_rect = SurroundingRectangle(
        _seq_surr_rect_g,
        color=GREY,
        buff=MED_SMALL_BUFF
    ).set_stroke(width=1, opacity=.7)
    seq_title = (
        Tex('Stream', font_size=25)
        .next_to(seq_surr_rect, UP, aligned_edge=UL)
    )

    self.add(seq_group, selection_square, seq_surr_rect, seq_title)

    ## DRAW THE TRACKERS ####################################################### DRAW TRACKERS
    recap_els = build_recap_els(
        ith_round=ith_round, 
        n_mem_els=MEMORY_SIZE - mem_list.count(None)
    )
    recap_ith_round, recap_p, recap_chi_size, recap_chi_over_p = recap_els

    recap_g = (
        Group(
            (
                Group(
                    Tex('Round', font_size=25),
                    recap_ith_round
                )
                .arrange(DOWN)
                .to_edge(LEFT)
            ), 
            (
                Group(
                    Tex('Sampling Probability', font_size=25),
                    recap_p
                )
                .arrange(DOWN)
            ),            
            (
                Group(
                    Tex('Elements in Memory', font_size=25),
                    recap_chi_size
                )
                .arrange(DOWN)
            ), 
            (
                Group(
                    Tex('Estimated Unique Values', font_size=25),
                    recap_chi_over_p
                )
                .arrange(DOWN)
            )
        )
        .arrange(DOWN, buff=.5)
        .next_to(title, DOWN, buff=.35)
        .to_edge(LEFT)
        .set_z_index(RECAP_Z_INDEX)
    )
    for g in recap_g:
        for el in g:
            el.to_edge(LEFT)

    recap_g_background = SurroundingRectangle(
        recap_g, 
        color=BLACK, fill_color=BLACK, fill_opacity=1,
        buff=LARGE_BUFF
    )
    recap_g_background.set_z_index(1)

    self.add(
        recap_g, 
        recap_g_background,
    )

    if only_setup:
        return

    ## MAIN ALGORITHM ########################################################## MAIN ALGORITHM
    run_time = 1
    run_time_fast = run_time / 2

    for ith_seq_el, (letter, seq_el_group) in enumerate(zip(SEQ[:first_els], seq_group)):
        
        self.play( 
            seq_group.animate.shift(LEFT * (SEQ_ELS_WIDTH + SEQ_ELS_SPACING)),

            run_time=run_time_fast
        )

        _seq_el_box, seq_el_letter, _seq_el_index = seq_el_group
        src_seq_letter: Text = seq_el_letter.copy()

        # if the current letter is already in the memory list,
        # remove it
        if letter in mem_list:
            to_pop_ix = mem_list.index(letter)
            self.play(
                Indicate(mem_els_letters[to_pop_ix], color=WHITE, scale_factor=1.75),
                Indicate(seq_el_letter, color=WHITE, scale_factor=1.75),

                run_time=run_time_fast
            )
            continue
        
            # remove from memory list
            mem_list[to_pop_ix] = None
            # play the fadeout, update the size tracker
            self.play(
                FadeOut(mem_els_letters[to_pop_ix], shift=UP),
                FadeOut(mem_els_ps[to_pop_ix], shift=UP),
                recap_chi_size.tracker.animate.set_value(MEMORY_SIZE - mem_list.count(None)),
                run_time=.5
            )
            # remove from scene
            self.remove(
                mem_els_letters[to_pop_ix],
                mem_els_ps[to_pop_ix]
            )
        
        # decide whether we should sample the current letter by tossing n coins
        # the number of coins depends on the round
        do_sample_current_letter = True
        
        pre_sampling_coins_group = (
            VGroup()
            .next_to(selection_square, DOWN)
            .align_to(selection_square)
        )
        sampling_coins_group = None
        for ith_coin in range(ith_round):
            # create a coin and place it under the letter
            letter_coin = SEQ_COIN_TEMPLATE.copy()

            # animate the coin spin
            _is_head = k_coin_tosser.toss()

            letter_coin_g = VGroup(letter_coin)
            sampling_coins_group = (
                pre_sampling_coins_group
                .copy()
                .add(letter_coin_g)
                .arrange(RIGHT, buff=SEQ_COIN_RADIUS/2)
            )
            sampling_coins_group.next_to(selection_square, DOWN)

            # remove the previous sampling animation
            self.play(FadeOut(pre_sampling_coins_group), run_time=.031)
            self.remove(pre_sampling_coins_group)
            
            # add the new sampling group
            self.add(sampling_coins_group)
            letter_coin = sampling_coins_group[-1]
            
            # determine the letter of the last coin
            letter_coin_text = (
                MathTex('H' if _is_head else 'T')
                .move_to(letter_coin.get_center())
            )
            letter_coin_text.add_updater(
                lambda o: o.move_to(letter_coin.get_center())
            )

            # play the animation
            self.play(
                AnimationGroup(
                    Rotate(letter_coin, angle=PI * 15, axis=RIGHT),
                    AnimationGroup(
                        letter_coin.animate.set_color(GREEN if _is_head else RED),
                        FadeIn(letter_coin_text),

                        lag_ratio=0
                    ),

                    run_time=run_time_fast,
                    lag_ratio=1
                )
            )

            # remember to add the coin letter to the group,
            # so that it can move
            letter_coin_g.add(letter_coin_text)

            # update the sampling group
            pre_sampling_coins_group = sampling_coins_group

            # if the spin returns tail, stop tossing coins
            if not _is_head:
                do_sample_current_letter = False
                break
            # otherwise color this one as green and toss another one
        
        # if it wasn't a win, go to the next letter
        if not do_sample_current_letter:
            self.play(
                FadeOut(sampling_coins_group), 
                FadeOut(pre_sampling_coins_group),
                run_time=0.031
            )
            self.remove(sampling_coins_group)
            self.remove(pre_sampling_coins_group)
            continue

        # otherwise, place the letter in the memory
        
        # find the box where it must go
        next_empty_box_ix = mem_list.index(None)
        dest_mem_box: Square = mem_els_boxes[next_empty_box_ix]
        dest_mem_pbox: Rectangle = mem_els_pboxes[next_empty_box_ix]
        # move the letter to the memory box
        dest_mem_letter = (
            src_seq_letter.copy()
            .scale(2)
            .set_color(YELLOW)
            .move_to(dest_mem_box.get_center())
        )
        dest_mem_p = (
            recap_p[1].copy()
            .scale(SMALL_P_SCALE_FACTOR)
            .move_to(dest_mem_pbox.get_center())
        )
        # place the letter in the memory list
        mem_list[next_empty_box_ix] = letter
        
        n_mem_els = MEMORY_SIZE - mem_list.count(None)
        new_recap_chi_size = (
            get_chi_size_formula(n_mem_els)
            .move_to(recap_chi_size.get_center())
            .to_edge(LEFT)
        )
        new_recap_chi_over_p = (
            get_chi_over_p_formula(n_mem_els, ith_round)
            .move_to(recap_chi_over_p.get_center())
            .to_edge(LEFT)
        )

        # animate the action
        self.play(
            # copy the sqe letter into the memory
            ReplacementTransform(src_seq_letter, dest_mem_letter),
            # copy the probability into the memory
            ReplacementTransform(recap_p[1].copy(), dest_mem_p),
            # update the memory size
            ReplacementTransform(recap_chi_size[-1], new_recap_chi_size[-1]),
            # update the estimated n unique els
            ReplacementTransform(recap_chi_over_p, new_recap_chi_over_p),

            run_time=run_time_fast
        )
        recap_chi_size = new_recap_chi_size
        recap_chi_over_p = new_recap_chi_over_p

        # keep track of the memory letter and p objects
        mem_els_letters[next_empty_box_ix] = dest_mem_letter
        mem_els_ps[next_empty_box_ix] = dest_mem_p
        
        # remove the sampling coins at the end of each iteration
        if ith_round > 0:
            self.play(
                FadeOut(pre_sampling_coins_group), 
                FadeOut(sampling_coins_group),
                run_time=0.031
            )
            self.remove(pre_sampling_coins_group)
            self.remove(sampling_coins_group)
        
        # if there is still room in the memory (at least a None), continue with the next letter 
        if mem_list.count(None) > 0:
            continue

        # otherwise memory is full!
        # full memory == next round

        # prune the memory
        removed_any = False
        while not removed_any:

            mem_pruning_coin = (
                MEM_COIN_TEMPLATE.copy()
                .next_to(mem_els_groups[-1], DOWN, buff=.3)
            )

            current_chi_over_p = recap_chi_over_p.copy()
            self.play(
                recap_chi_over_p.animate.set_color(GREY),
                
                run_time=run_time_fast
            )

            mem_pruning_coin_text = None
            for ith_ml, ml in enumerate(mem_list[::-1], 1):
                
                if ith_ml > 1:
                    # shift the coin under the next element in the memory
                    # and update the color
                    self.remove(mem_pruning_coin_text)
                    mem_pruning_coin.next_to(mem_els_groups[-ith_ml], DOWN, buff=.3)
                    mem_pruning_coin.set_color(COIN_COLOR)

                _is_head = one_coin_pgen.toss()

                mem_pruning_coin_text = (
                    MathTex('H' if _is_head else 'T')
                    .move_to(mem_pruning_coin.get_center())
                )

                # animate the rotation and the color change
                self.play(AnimationGroup(
                    # flip the coin
                    Rotate(mem_pruning_coin, angle=PI * 10, axis=RIGHT),
                    # change the color based on head/tail
                    AnimationGroup(
                        mem_pruning_coin.animate.set_color(GREEN if _is_head else RED),
                        FadeIn(mem_pruning_coin_text),
                        
                        lag_ratio=0
                    ),

                    run_time=run_time_fast,
                    lag_ratio=1
                ))
                
                # toss a coin, if tail remove the letter from the memory
                if not _is_head:
                    # if heads, remove it
                    # find the index of the element to remove
                    to_pop_ix = mem_list.index(ml)
                    # remove the letter from the memory list
                    mem_list[to_pop_ix] = None

                    n_mem_els = MEMORY_SIZE - mem_list.count(None)
                    new_recap_chi_size = (
                        get_chi_size_formula(n_mem_els)
                        .move_to(recap_chi_size.get_center())
                        .to_edge(LEFT)
                    )

                    self.play(
                        # play the fadeout of the letter and its prob
                        FadeOut(mem_els_letters[to_pop_ix], shift=UP),
                        FadeOut(mem_els_ps[to_pop_ix], shift=UP),
                        # update the memory size
                        ReplacementTransform(recap_chi_size[-1], new_recap_chi_size[-1]),

                        run_time=run_time_fast
                    )

                    recap_chi_size = new_recap_chi_size
                    # recap_chi_over_p = new_recap_chi_over_p

                    # remove letter and probability from drawing
                    self.remove(
                        mem_els_letters[to_pop_ix],
                        mem_els_ps[to_pop_ix]
                    )
                    mem_els_letters[to_pop_ix] = None
                    mem_els_ps[to_pop_ix] = None
                    
                    # record that at least one element was removed from the memory
                    removed_any = True

                # if it's heads, half the current prob
                else:
                    current_p = mem_els_ps[-ith_ml]
                    new_p = (
                        get_p_formula(ith_round=ith_round+1)
                        [1]
                        .scale(SMALL_P_SCALE_FACTOR)
                        .set_color(GREY)
                        .move_to(current_p.get_center())
                    )
                    mem_els_ps[-ith_ml] = new_p

                    n1_2 = (
                        MathTex('1/2')
                        .set_stroke(GREY)
                        .scale(SMALL_P_SCALE_FACTOR)
                        .move_to(mem_pruning_coin.get_center())
                    )
                    n1_2.generate_target()
                    n1_2.target.move_to(new_p.get_center())

                    self.play(
                        AnimationGroup(
                            AnimationGroup(
                                Create(n1_2, lag_ratio=0),
                                AnimationGroup(MoveToTarget(n1_2), FadeOut(n1_2), lag_ratio=.9),
                                lag_ratio=0
                            ),
                            ReplacementTransform(current_p, new_p),
                            lag_ratio=.1
                        ),
                        
                        run_time=run_time_fast
                    )

            # remove the memory coin after the memory is pruned
            self.remove(mem_pruning_coin, mem_pruning_coin_text)

            # recolor chi over p
            self.play(
                recap_chi_over_p.animate.match_style(current_chi_over_p),
                run_time=run_time_fast
            )

        # update the round number, the probability and the texts
        ith_round += 1
        p = p / 2
        k_coin_tosser = RegularCoinSequenceTosser(k=ith_round)
        
        new_recap_ith_round = (
            get_ith_round_formula(ith_round)
            .move_to(recap_ith_round.get_center())
            .to_edge(LEFT)
        )
        new_recap_p = (
            get_p_formula(ith_round)
            .move_to(recap_p.get_center())
            .to_edge(LEFT)
        )
        new_recap_chi_over_p = (
            get_chi_over_p_formula(n_mem_els, ith_round)
            .move_to(recap_chi_over_p.get_center())
            .to_edge(LEFT)
        )

        self.play(
            ReplacementTransform(recap_ith_round, new_recap_ith_round),
            ReplacementTransform(recap_p, new_recap_p),
            ReplacementTransform(recap_chi_over_p, new_recap_chi_over_p),
            *[
                g.animate.set_color(BLUE)
                for g in mem_els_ps
                if g is not None
            ],

            run_time=run_time
        )

        recap_ith_round = new_recap_ith_round
        recap_p = new_recap_p
        recap_chi_over_p = new_recap_chi_over_p

        run_time = max(run_time * .75, 0.035)
        run_time_fast = max(run_time * .5, 0.035)
        
    self.wait()
    
