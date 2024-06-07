from manim import *
from manim import config as mn_config
import random
import string
from typing import Optional, List

mn_config.media_width = "75%"
mn_config.verbosity = "WARNING"


STREAM_LEN = 50
random.seed(STREAM_LEN)
MEMORY_SIZE = 5

# colors
COIN_COLOR = YELLOW_E
P_COLOR = BLUE
ROUND_COLOR = LIGHT_PINK
MEMORY_COLOR = YELLOW

SMALL_P_SCALE_FACTOR = .75

# z-indices
STREAM_Z_INDEX = 1
RECAP_Z_INDEX = 5

# constants for the sequence
STREAM_ELS_WIDTH = .75
STREAM_ELS_SPACING = .05
STREAM_COIN_RADIUS = STREAM_ELS_WIDTH / 2 * .75
STREAM_COIN_TEMPLATE = (
    Circle(radius=STREAM_COIN_RADIUS, color=COIN_COLOR, fill_opacity=1)
    .set_stroke(color=BLACK, width=1)
)
# constants for the memory
MEM_ELS_WIDTH = 1.15
MEM_ELS_SPACING = MEM_ELS_WIDTH * 1.15
MEM_COIN_RADIUS = STREAM_COIN_RADIUS
MEM_COIN_TEMPLATE = (
    Circle(radius=MEM_COIN_RADIUS, color=COIN_COLOR, fill_opacity=1)
    .set_stroke(color=BLACK, width=1)
)


def build_ascii_seq(stream_len: int) -> str:
    while True:
        seq = ''.join([random.choice(string.ascii_uppercase) for _ in range(stream_len)])
        if len(set(seq)) == len(set(string.ascii_uppercase)):
            return seq

STREAM = build_ascii_seq(STREAM_LEN)

class RegularCoinSequenceTosser:
    """
    Create a non-random coin tosser that returns a sequence of k heads
    at regular intervals. 
    
    If k = 1, then we generate 1H every 2**1 tosses.
    If k = 2, then we generate 2H every 2**2 tosses.
    ...
    
    The idea is that since it is only a simulation,
    if the coin behaves as expected it helps understanding its implied probability.
    """

    def __init__(self, k) -> None:
        self.k = k
        self._mod = 2**k
        self._index = 0
        self._g_index = 0

    def toss(self) -> int:
        "Toss the coin one more time. Return 0 (tails) or 1 (heads)"

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


class Formula:

    def get_round_k_formula(round_k: int) -> MathTex:
        "Draw the formula for the round"
        f = MathTex(r'k = ', f'{round_k}')
        f.set_z_index(RECAP_Z_INDEX)
        f[-1].set_color(ROUND_COLOR).set_stroke(width=2)
        return f


    def get_p_formula(round_k: int) -> MathTex:
        """Draw the formula for the sampling probability"""
        f = MathTex(
            r'p =', 
            (r'1/' + f'{2**round_k}') if round_k != 0 else r'1', 
            r' = \left( \frac{1}{2} \right)^{', 
            f'{round_k}', 
            r'} = ',
            r'P\left(',
            r'\frac{' + str(round_k) + r'H}{',
            str(round_k),
            r'\text{ tosses}',
            r'}\right)'
        )
        f.set_z_index(RECAP_Z_INDEX)
        f[1].set_stroke(width=2).set_color(BLUE)
        # if the probability is not exactly 1, then scale the 1/ of the fraction
        # because it keeps the formula tighter and it also looks better 
        if round_k != 0:
            f[1][2:].next_to(f[1][0], RIGHT, buff=0)
            f[1][:2].scale(.5).shift(UL*.15)
        f[2:].set_color(GREY)
        f[3].set_stroke(width=1).set_color(LIGHT_PINK)
        f[6][:-2].set_stroke(width=1).set_color(LIGHT_PINK)
        f[6][-2].set_stroke(width=1).set_color(GREEN)
        f[7].set_stroke(width=1).set_color(LIGHT_PINK)
        f[2:].scale(.5).next_to(f[:2], RIGHT)
        return f


    def get_chi_size_formula(memcount: int) -> MathTex:
        """Draw the formula for the memory count"""
        f = MathTex(r'|X|', '=', f'{memcount}')
        f.set_z_index(RECAP_Z_INDEX)
        f[-1].set_stroke(width=2).set_color(YELLOW)
        return f


    def get_memcount_over_p_formula(memsize, round_k):
        "Draw the formula for the unique elements estimated count."
        f = MathTex(
            r'\frac{|X|}{p}', 
            '=', 
            r'\frac{' + str(memsize) + r'}{' + (
                (r'1/' if round_k != 0 else '') + f'{2**round_k}' + r'}'
            ),
            r'=', 
            f'{memsize * 2**round_k}'
        )
        f.set_z_index(RECAP_Z_INDEX)
        num = f[-3][0]
        num.set_stroke(width=2).set_color(YELLOW)
        den = f[-3][2:]
        den.set_stroke(width=2).set_color(BLUE)
        # if the probability is not exactly 1, then scale the 1/ of the fraction
        # because it keeps the formula tighter and it also looks better 
        if round_k != 0:
            den[2:].next_to(f[-3][2], RIGHT, buff=0)
            den[:2].scale(.5).shift(UL*.15)
            den.set_x(num.get_x())
        return f


def draw_stream(self: Scene, n_els=STREAM_LEN):
    """Helper function that builds all the visual and auxiliary components 
    related to the "stream" area of the animation.
    """

    stream_els_groups: List[VGroup] = []
    stream_letters: List[Text] = []
    
    # for each element in the sequence, create some visual elements
    for ith_stream_el, stream_el_str in enumerate(STREAM[:n_els]):
        
        # create a box
        a_stream_el_box = (
            Square(side_length=STREAM_ELS_WIDTH)
            .set_stroke(width=1)
        )

        # create the letter inside
        a_stream_letter = (
            Text(stream_el_str, font_size=17)
            .move_to(a_stream_el_box.get_center())
        )
        
        # create the index above the box
        a_stream_ix = (
            Text(str(ith_stream_el), font_size=10)
            .next_to(a_stream_el_box, UP, buff=.2)
        )

        # create a vgroup (box + letter + index)
        a_stream_el_group = VGroup(a_stream_el_box, a_stream_letter, a_stream_ix)
        
        # add the vgroup to the scene
        self.add(a_stream_el_box, a_stream_letter, a_stream_ix)

        # keep track of the elements
        stream_letters.append(a_stream_letter)
        stream_els_groups.append(a_stream_el_group)

    # move / transform the group
    stream_group = (
        VGroup(*stream_els_groups)
        .arrange(buff=STREAM_ELS_SPACING)
        .align_to(self.camera.frame_center, LEFT)
        .shift(1.85*UP + ORIGIN)
        .shift(RIGHT * (STREAM_ELS_WIDTH + STREAM_ELS_SPACING))
        .set_z_index(STREAM_Z_INDEX)
    )

    # move / transform the selector square
    stream_selector_square = (
        Square(side_length=STREAM_ELS_WIDTH * 1.1)
        .set_stroke(color=RED_C, width=5)
        .move_to(stream_group[0][0].get_center())
        .shift(LEFT * (STREAM_ELS_WIDTH + STREAM_ELS_SPACING))
    )

    # create a surrounding rectangle
    # create these hidden elements to determine the appropriate size for the rectangle
    _stream_surr_rect_g = Group(
        stream_selector_square.copy()
        .shift(LEFT * (STREAM_ELS_SPACING + STREAM_ELS_WIDTH) * .6).set_opacity(0),
        stream_selector_square.copy()
        .shift(RIGHT * (STREAM_ELS_SPACING + STREAM_ELS_WIDTH) * 6.35).set_opacity(0),
        stream_group[0][-1].copy()
        .set_opacity(0),
        STREAM_COIN_TEMPLATE.copy()
        .next_to(stream_selector_square, DOWN).set_opacity(0),
    )
    # create the actual rectangle
    stream_surr_rect = (
        SurroundingRectangle(
            _stream_surr_rect_g,
            color=GREY,
            buff=MED_SMALL_BUFF
        )
        .set_stroke(width=1, opacity=.7)
    )
    # place a title on top of it
    stream_title = (
        Tex('Stream', font_size=25)
        .next_to(stream_surr_rect, UP, aligned_edge=UL)
    )

    self.add(stream_group, stream_selector_square, stream_surr_rect, stream_title)

    return stream_group, stream_selector_square, stream_surr_rect, stream_title



def draw_recap_section(self: Scene, round_k: int, n_mem_els: int, scene_title: MathTex):
    """Helper function that builds all the visual and auxiliary components 
    related to the "recap" area of the animation.
    """

    recap_round_k = Formula.get_round_k_formula(round_k)
    recap_p = Formula.get_p_formula(round_k)
    recap_chi_size = Formula.get_chi_size_formula(n_mem_els)
    recap_chisize_over_p = Formula.get_memcount_over_p_formula(n_mem_els, round_k)

    recap_g = (
        Group(
            (
                Group(
                    Tex('Round', font_size=25),
                    recap_round_k
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
                    recap_chisize_over_p
                )
                .arrange(DOWN)
            )
        )
        .arrange(DOWN, buff=.5)
        .next_to(scene_title, DOWN, buff=.35)
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

    return (
        recap_g, 
        recap_g_background,
        recap_round_k,
        recap_p,
        recap_chi_size,
        recap_chisize_over_p,
    )
        

def draw_memory(self: Scene):

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

    # add a small X and p_x texts on the left side of the memory
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

    # add a surrounding rectangle around the memory
    # include a hidden coin below it to create room for the flippin coin
    _hidden_pruning_coin = (
        MEM_COIN_TEMPLATE.copy()
        .next_to(mem_els_groups[-1], DOWN, buff=.3)
    )
    mem_group.add(_hidden_pruning_coin.copy().set_opacity(0))
    mem_surr_rect = (
        SurroundingRectangle(
        mem_group,
            color=GREY,
            buff=MED_SMALL_BUFF
        )
        .set_stroke(width=1, opacity=.7)
    )

    # add a title to the surrounding rectangle
    mem_title = (
        Tex('Memory', font_size=25)
        .next_to(mem_surr_rect, UP, aligned_edge=UL)
    )

    self.add(
        mem_group, 
        mem_surr_rect,
        mem_title,
    )

    return (
        mem_group,
        mem_els_groups,
        mem_els_boxes,
        mem_els_pboxes
    )


def sample_stream_element(
    self: Scene, 
    round_k: int, 
    coin_tosser: RegularCoinSequenceTosser, 
    stream_selector_square: Square,
    run_time: float,
):
    """Implement the logic of tossing coins to determine whether an element
    should be sampled into memory or not."""

    # decide whether we should sample the current letter by tossing n coins
    # the number of coins depends on the round
    do_sample_current_letter = True
    
    pre_sampling_coins_group = (
        VGroup()
        .next_to(stream_selector_square, DOWN)
        .align_to(stream_selector_square)
    )
    sampling_coins_group = None

    # toss at most k coins
    for ith_coin in range(round_k):

        # create a coin and place it under the letter
        letter_coin = STREAM_COIN_TEMPLATE.copy()
        letter_coin_g = VGroup(letter_coin)

        # update the group of coins so it has one more coin
        sampling_coins_group = (
            pre_sampling_coins_group
            .copy()
            .add(letter_coin_g)
            .arrange(RIGHT, buff=-STREAM_COIN_RADIUS/2)
        )
        sampling_coins_group.next_to(stream_selector_square, DOWN)

        # animate the removal of the previous coins group
        self.play(FadeOut(pre_sampling_coins_group), run_time=0.04)
        self.remove(pre_sampling_coins_group)
        
        # add the new sampling group
        self.add(sampling_coins_group)
        letter_coin = sampling_coins_group[-1]
        
        # toss the coin
        _is_head = coin_tosser.toss()
        # determine the letter of the last coin
        letter_coin_text = (
            MathTex('H' if _is_head else 'T')
            .move_to(letter_coin.get_center())
        )
        letter_coin_text.add_updater(
            lambda o: o.move_to(letter_coin.get_center())
        )

        # play the toss animation
        self.play(
            AnimationGroup(
                # rotate
                Rotate(letter_coin, angle=PI * 15, axis=RIGHT),
                # change color
                AnimationGroup(
                    letter_coin.animate.set_color(GREEN if _is_head else RED),
                    # fade in H or T
                    FadeIn(letter_coin_text),

                    lag_ratio=0
                ),

                run_time=run_time,
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
            break
        # otherwise toss another one
    
    return do_sample_current_letter, sampling_coins_group, pre_sampling_coins_group
    

def cvm_algorithm(
    self: Scene, 
    only_setup=False, 
    n_stream_els=None, 
    animate_first_n_els=None, 
    seed=0
):
    """
    Main function.
    only_setup: whether only the setup should be drawn, without the algorithm animation.
    n_stream_els: how many elements of the stream should be included in the animation. max 100.
    animate_first_n_els: how many iterations should be animated
    seed: seed for random events
    """

    random.seed(seed)

    if n_stream_els is None:
        n_stream_els = STREAM_LEN
    if animate_first_n_els is None:
        animate_first_n_els = n_stream_els
    n_stream_els = min(100, n_stream_els)
    animate_first_n_els = min(n_stream_els, animate_first_n_els)

    # start with probability 1, round 0
    p = 1
    round_k = 0

    # instantiate random events generators
    k_coin_tosser = RegularCoinSequenceTosser(k=round_k)    # for the stream
    one_coin_pgen = RegularCoinSequenceTosser(k=1)          # for clearing the memory (fixed p=1/2)

    # instantiate the memory; keep track of
    # - the raw letters (str)
    # - the drawn letters (Text)
    # - the drawn probabilities values (Text)
    mem_list: List[Optional[str]]           = [None for _ in range(MEMORY_SIZE)]
    mem_els_letters: List[Optional[Text]]   = [None for _ in range(MEMORY_SIZE)]
    mem_els_ps: List[Optional[Text]]        = [None for _ in range(MEMORY_SIZE)]

    ## DRAW TITLE ############################################################## DRAW TITLE
    scene_title = (
        Tex(r"\underline{\textbf{CVM Algorithm}}")
        .to_edge(UL)
    )
    scene_title.set_z_index(RECAP_Z_INDEX)
    self.add(scene_title)

    ## DRAW THE MEMORY ######################################################### DRAW THE MEMORY
    (
        _,
        mem_els_groups,
        mem_els_boxes,
        mem_els_pboxes,
    ) = draw_memory(self)

    ## DRAW THE SEQUENCE ####################################################### DRAW THE SEQUENCE
    (
        stream_group, 
        stream_selector_square, 
        _, 
        _
    ) = draw_stream(self, n_els=n_stream_els)

    ## DRAW THE RECAP ########################################################## DRAW THE RECAP
    (
        recap_g, 
        _,
        recap_round_k,
        recap_p,
        recap_chi_size,
        recap_chisize_over_p
    ) = draw_recap_section(
        self,
        round_k=round_k, 
        n_mem_els=MEMORY_SIZE - mem_list.count(None),
        scene_title=scene_title
    )

    # terminate if only the setup is requested
    if only_setup:
        return

    ## MAIN ALGORITHM ########################################################## MAIN ALGORITHM

    for letter, stream_el_group in zip(STREAM[:animate_first_n_els], stream_group):

        # set the run times
        _run_time = max(1 * (.8 ** round_k), 0.04)
        _run_time_fast = max(_run_time * .8, 0.04)
        
        # shift the stream to the left
        self.play( 
            stream_group.animate.shift(LEFT * (STREAM_ELS_WIDTH + STREAM_ELS_SPACING)),

            run_time=_run_time_fast
        )
        
        _stream_el_box, stream_el_letter, _stream_el_index = stream_el_group
        src_stream_letter: Text = stream_el_letter.copy()

        # if the current letter is already in the memory list,
        # remove it
        if letter in mem_list:
            to_pop_ix = mem_list.index(letter)
            self.play(
                Indicate(mem_els_letters[to_pop_ix], color=WHITE, scale_factor=1.75),
                Indicate(stream_el_letter, color=WHITE, scale_factor=1.75),

                run_time=_run_time_fast
            )
            continue
        
        # if the letter is not in the memory
        # decide whether to sample it
        do_sample, sampling_coins_group, pre_sampling_coins_group = sample_stream_element(
            self,
            round_k=round_k,
            coin_tosser=k_coin_tosser,
            stream_selector_square=stream_selector_square,
            run_time=_run_time_fast
        )
        # if not sampling, fade out the sampling coins, 
        # move to the next element in the stream
        if not do_sample:
            # if it wasn't a win, go to the next letter
            self.play(
                FadeOut(sampling_coins_group, run_time=0.04), 
                FadeOut(pre_sampling_coins_group, run_time=0.04),
                
            )
            self.remove(sampling_coins_group)
            self.remove(pre_sampling_coins_group)
            continue
        # otherwise, place the element in the memory
        
        # find the box where it must go
        next_empty_box_ix = mem_list.index(None)
        dest_mem_box: Square = mem_els_boxes[next_empty_box_ix]
        dest_mem_pbox: Rectangle = mem_els_pboxes[next_empty_box_ix]

        # move the letter to the memory box
        dest_mem_letter = (
            src_stream_letter.copy()
            .scale(2)
            .set_color(MEMORY_COLOR)
            .move_to(dest_mem_box.get_center())
        )
        dest_mem_p = (
            recap_p[1].copy()
            .scale(SMALL_P_SCALE_FACTOR)
            .move_to(dest_mem_pbox.get_center())
        )
        # place the letter in the memory list
        mem_list[next_empty_box_ix] = letter
        
        # update the recap formulas
        n_mem_els = MEMORY_SIZE - mem_list.count(None)
        new_recap_chi_size = (
            Formula.get_chi_size_formula(n_mem_els)
            .move_to(recap_chi_size.get_center())
            .to_edge(LEFT)
        )
        new_recap_chisize_over_p = (
            Formula.get_memcount_over_p_formula(n_mem_els, round_k)
            .move_to(recap_chisize_over_p.get_center())
            .to_edge(LEFT)
        )

        # animate the action
        self.play(
            # copy the sqe letter into the memory
            ReplacementTransform(src_stream_letter, dest_mem_letter),
            # copy the probability into the memory
            ReplacementTransform(recap_p[1].copy(), dest_mem_p),
            # update the memory size
            ReplacementTransform(recap_chi_size[-1], new_recap_chi_size[-1]),
            # update the estimated n unique els
            ReplacementTransform(recap_chisize_over_p, new_recap_chisize_over_p),

            run_time=_run_time_fast
        )
        recap_chi_size = new_recap_chi_size
        recap_chisize_over_p = new_recap_chisize_over_p

        # keep track of the memory letter and p objects
        mem_els_letters[next_empty_box_ix] = dest_mem_letter
        mem_els_ps[next_empty_box_ix] = dest_mem_p
        
        # remove the sampling coins at the end of each iteration
        if round_k > 0:
            self.play(
                FadeOut(pre_sampling_coins_group, run_time=0.04), 
                FadeOut(sampling_coins_group, run_time=0.04),
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
        # the original algorithm fails if no elements are removed
        # here include a while that ensures at least one element is removed
        while not removed_any:
            
            # instantiate a coin
            mem_pruning_coin = (
                MEM_COIN_TEMPLATE.copy()
                .next_to(mem_els_groups[-1], DOWN, buff=.3)
            )

            # "freeze" the size over p formula until pruning is complete
            # so color the formula in grey
            current_chisize_over_p = recap_chisize_over_p.copy()
            self.play(
                recap_chisize_over_p.animate.set_color(GREY),
                
                run_time=_run_time_fast
            )

            # visit all the elements of the memory 
            # (backwards, because I prefer visually...)
            mem_pruning_coin_text = None
            for ith_ml, ml in enumerate(mem_list[::-1], 1):
                
                if ith_ml > 1:
                    # shift the coin under the next element in the memory
                    # and update the color
                    self.remove(mem_pruning_coin_text)
                    mem_pruning_coin.next_to(mem_els_groups[-ith_ml], DOWN, buff=.3)
                    mem_pruning_coin.set_color(COIN_COLOR)

                # toss the coin and determine the letter
                is_toss_head = one_coin_pgen.toss()
                mem_pruning_coin_text = (
                    MathTex('H' if is_toss_head else 'T')
                    .move_to(mem_pruning_coin.get_center())
                )

                # animate the rotation and the color change
                self.play(AnimationGroup(
                    # flip the coin
                    Rotate(mem_pruning_coin, angle=PI * 10, axis=RIGHT),
                    # change the color based on head/tail
                    AnimationGroup(
                        mem_pruning_coin.animate.set_color(GREEN if is_toss_head else RED),
                        FadeIn(mem_pruning_coin_text),
                        
                        lag_ratio=0
                    ),

                    run_time=_run_time_fast,
                    lag_ratio=1
                ))
                
                # if tail remove the letter from the memory
                if not is_toss_head:

                    # find the index of the element to remove
                    to_pop_ix = mem_list.index(ml)
                    # remove the letter from the memory list
                    mem_list[to_pop_ix] = None

                    # update the memory size formula
                    n_mem_els = MEMORY_SIZE - mem_list.count(None)
                    new_recap_chi_size = (
                        Formula.get_chi_size_formula(n_mem_els)
                        .move_to(recap_chi_size.get_center())
                        .to_edge(LEFT)
                    )

                    # play the animation
                    self.play(
                        # play the fadeout of the letter and its prob
                        FadeOut(mem_els_letters[to_pop_ix], shift=UP, run_time=0.04),
                        FadeOut(mem_els_ps[to_pop_ix], shift=UP, run_time=0.04),
                        # update the memory size
                        ReplacementTransform(recap_chi_size[-1], new_recap_chi_size[-1]),

                        run_time=_run_time_fast
                    )

                    recap_chi_size = new_recap_chi_size

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

                    # get the current p
                    current_p = mem_els_ps[-ith_ml]
                    # the new is the same as the p of the formula in the next round
                    new_p = (
                        Formula.get_p_formula(round_k=round_k+1)
                        [1]
                        .scale(SMALL_P_SCALE_FACTOR)
                        .set_color(GREY)
                        .move_to(current_p.get_center())
                    )
                    mem_els_ps[-ith_ml] = new_p

                    # animate a 1/2 moving from the pruning coin to the 
                    # sampling probability associated to the element in the memory
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
                                # create the 1/2
                                Create(n1_2, lag_ratio=0),
                                # move it to the probability box
                                AnimationGroup(MoveToTarget(n1_2), FadeOut(n1_2, run_time=0.04), lag_ratio=.9),
                                lag_ratio=0,
                                
                                run_time=_run_time_fast
                            ),

                            # transform the old probability of the memory element
                            # to the new one
                            ReplacementTransform(current_p, new_p, run_time=_run_time_fast),

                            lag_ratio=.1
                        ),
                    )

            # remove the memory coin after the memory is pruned
            self.remove(mem_pruning_coin, mem_pruning_coin_text)

            # recolor chi over p
            self.play(
                recap_chisize_over_p.animate.match_style(current_chisize_over_p),
                run_time=_run_time_fast
            )

        # after pruning the memory
        # update the round number, the probability and all the recap
        round_k += 1
        p = p / 2
        k_coin_tosser = RegularCoinSequenceTosser(k=round_k)
        
        new_recap_round_k = (
            Formula.get_round_k_formula(round_k)
            .move_to(recap_round_k.get_center())
            .to_edge(LEFT)
        )
        new_recap_p = (
            Formula.get_p_formula(round_k)
            .move_to(recap_p.get_center())
            .to_edge(LEFT)
        )
        new_recap_chisize_over_p = (
            Formula.get_memcount_over_p_formula(n_mem_els, round_k)
            .move_to(recap_chisize_over_p.get_center())
            .to_edge(LEFT)
        )

        # animate the values updates
        self.play(
            ReplacementTransform(recap_round_k, new_recap_round_k),
            ReplacementTransform(recap_p, new_recap_p),
            ReplacementTransform(recap_chisize_over_p, new_recap_chisize_over_p),

            # all the memory elements probabilities now turn blue
            *[
                g.animate.set_color(BLUE)
                for g in mem_els_ps
                if g is not None
            ],

            run_time=_run_time
        )

        recap_round_k = new_recap_round_k
        recap_p = new_recap_p
        recap_chisize_over_p = new_recap_chisize_over_p
        
    self.wait()
    

class CVM(Scene):
    def construct(self):
        cvm_algorithm(self)


if __name__ == '__main__':
    pass