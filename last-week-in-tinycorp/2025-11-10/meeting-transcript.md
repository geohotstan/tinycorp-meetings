# NOTE


# 2025-11-10 Meeting

### Meeting Agenda

**Time:** 9am Monday San Diego time, 1am Hong Kong time
- AMD CONTRACT!!!!!!!
- CDNA4/RDNA3 SQTT in VIZ, same view as RGP
- apple usb gpu without SIP bypass. i bought 3x 5060 for mac CI machines
- why is progress on tinykittens so slow? if it can't do a SOTA gemm, we should look elsewhere
- LLaMA trainer using custom_kernel to get memory usage to acceptable place, figure out what kernels we need to write
- openpilot regressions
- other bounties

### Audio

[Youtube Link](https://www.youtube.com/watch?v=VsR6zf1bJrw)

### Highlights

- **[Company Update](#geohot-000022)**: A new product, the Tenubox Green, was launched for users who need a lot of VRAM. One unit has been sold so far.
- **[AMD Contract is Top Priority](#geohot-000305)**: Geohot declares that the entire company must focus on the AMD contract, stating that if they cannot succeed in training a large LLaMA model on modern hardware, he will shut the company down.
- **[Debate on Company Direction](#chenyu-000906)**: A lengthy debate occurs about the value and motivation behind the AMD contract. Chenyu questions its strategic importance, while Geohot argues it's a crucial test to prove TinyGrad's performance and advance the framework, which is currently "hopelessly slow."
- **[Writing Custom Kernels vs. Search](#geohot-002331)**: Geohot justifies the need to hand-code kernels for the contract, arguing that it's necessary for short-term performance and to ensure the UOP language can express state-of-the-art techniques, which will inform future automated search improvements.
- **[SQTT Visualization and Tooling](#geohot-002916)**: The team discusses issues with SQTT visualization in VIZ, noting discrepancies with AMD's RGP tool. The current decoder is seen as "unmaintained crap," leading to a plan to compare results with `rockprof` and eventually write a custom SQTT parser.
- **[TinyKittens Gemm Performance](#geohot-003637)**: Progress on the TinyKittens project is slow; while indexing logic is correct, optimizations like local swizzling are disabled, causing performance hits. Geohot emphasizes the need to achieve state-of-the-art gemm speed.
- **[AMD FP8 Training Progress](#chenyu-004702)**: Progress has been made on FP8 training by selectively quantizing Q and K tensors, which allows the loss to decrease. Next steps include using faster tensor cores and debugging a multi-GPU OOM error.
- **[Future of TinyGrad and Market Position](#geohot-005555)**: Geohot gives TinyGrad a 20% chance of becoming the dominant framework on AMD hardware in three years, but a near-zero chance on NVIDIA. This sparks a debate about the factors driving framework adoption and which ecosystems are the best to target.
- **[AMD Contract Plan](#geohot-011114)**: Geohot outlines a plan for the contract, breaking the work into four parallel streams: the high-level trainer, custom kernel implementation, data movement, and visualization. He will start by writing stub kernels to analyze memory usage for the LLaMA trainer.

### Transcript
##### **Geohot** [[00:00:00](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=0)]
Let's get started. Hello, everyone.

##### **Geohot** [[00:00:04](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4)]
We should do something to the meeting number as we approach 100.

##### **Geohot** [[00:00:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=7)]
That was too much.

##### **Geohot** [[00:00:09](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=9)]
Yeah, we'll just start calling it one again.

##### **Geohot** [[00:00:11](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=11)]
Yes.

##### **Chenyu** [[00:00:11](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=11)]
New meeting number one.

##### **Geohot** [[00:00:13](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=13)]
Yes.

##### **Geohot** [[00:00:13](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=13)]
Call it new meeting.

##### **Geohot** [[00:00:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=14)]
Great.

##### **Geohot** [[00:00:15](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=15)]
Maybe we'll change the style though.

##### **Geohot** [[00:00:16](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=16)]
Oh, yeah, we'll see.

##### **Chenyu** [[00:00:17](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=17)]
Yeah.

##### **Geohot** [[00:00:18](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=18)]
Okay.

##### **Geohot** [[00:00:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=19)]
Let's start with company update.

##### **Geohot** [[00:00:22](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=22)]
So we launched a new product this week.

##### **Geohot** [[00:00:24](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=24)]
We got the Tenubox Green overpriced edition for people who love VRAM.

##### **Geohot** [[00:00:30](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=30)]
It's not really overpriced.

##### **Chenyu** [[00:00:31](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=31)]
It's a pretty good deal.

##### **Geohot** [[00:00:32](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=32)]
We sold one so far.

##### **Geohot** [[00:00:35](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=35)]
So, yeah.

##### **Geohot** [[00:00:40](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=40)]
I don't know.

##### **Geohot** [[00:00:41](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=41)]
I tried some new marketing with a product for the GPU middle class.

##### **Geohot** [[00:00:47](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=47)]
We'll see if that works.

##### **Chenyu** [[00:00:48](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=48)]
Yeah, I don't want everything but the kitchen sink.

##### **Geohot** [[00:00:50](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=50)]
I don't want libraries like this polluting the repo.

##### **Geohot** [[00:00:55](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=55)]
So, yeah.

##### **Geohot** [[00:00:56](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=56)]
We'll get to that later.

##### **Geohot** [[00:00:57](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=57)]
Okay.

##### **Geohot** [[00:00:59](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=59)]
Are we still doing the NanoChat training this Monday?

##### **Chenyu** [[00:01:04](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=64)]
If he's down, I'm down.

##### **Geohot** [[00:01:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=66)]
I thought he already surrendered.

##### **Geohot** [[00:01:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=67)]
But if he's down, I'm so down.

##### **Geohot** [[00:01:09](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=69)]
Let's go.

##### **Geohot** [[00:01:10](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=70)]
I'll even have the machine too.

##### **Geohot** [[00:01:11](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=71)]
We ordered the GPUs.

##### **Chenyu** [[00:01:13](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=73)]
We ordered for the RTX 6000 Blackwell Pros.

##### **Geohot** [[00:01:18](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=78)]
So we'll have both machines.

##### **Geohot** [[00:01:20](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=80)]
Happy to benchmark it.

##### **Geohot** [[00:01:22](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=82)]
You know, look.

##### **Geohot** [[00:01:23](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=83)]
Am I really trying to take this?

##### **Geohot** [[00:01:24](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=84)]
I'm going to take 10K from some Twitter in on.

##### **Chenyu** [[00:01:26](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=86)]
It depends how rich he is.

##### **Geohot** [[00:01:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=87)]
If it turns out he got big rich in some startup, yeah, I'll take his 10K.

##### **Geohot** [[00:01:30](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=90)]
If he's like some kid, I'm going to take his 10K.

##### **Geohot** [[00:01:35](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=95)]
Yeah.

##### **Geohot** [[00:01:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=97)]
But, no, I think the other thing that I want to talk about for this meeting is I'm basically here to support the four of you for whatever you need to get the contract done.

##### **Geohot** [[00:01:49](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=109)]
And have me do things that nobody else knows how to do.

##### **Chenyu** [[00:01:53](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=113)]
Or.

##### **Geohot** [[00:01:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=114)]
If there's nothing pressing, I could also focus on just general testing, stability, mutation, fuzzing.

##### **Geohot** [[00:02:03](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=123)]
Like people, you know, just general bug and cleanups.

##### **Geohot** [[00:02:09](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=129)]
But, yeah.

##### **Geohot** [[00:02:10](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=130)]
I mean, I think it's really going to come down to what any of the four of you need.

##### **Geohot** [[00:02:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=134)]
Because I think every part should be covered.

##### **Chenyu** [[00:02:16](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=136)]
Yeah.

##### **Geohot** [[00:02:17](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=137)]
We just need a drive to do the contract.

##### **Geohot** [[00:02:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=139)]
What do you mean?

##### **Geohot** [[00:02:20](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=140)]
A drive.

##### **Geohot** [[00:02:22](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=142)]
You're the one that's most excited about it.

##### **Geohot** [[00:02:24](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=144)]
The contract.

##### **Chenyu** [[00:02:25](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=145)]
The contract's sick.

##### **Geohot** [[00:02:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=147)]
Yeah, that's the difference.

##### **Geohot** [[00:02:28](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=148)]
What's wrong with the contract?

##### **Geohot** [[00:02:30](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=150)]
The drive to do the contract.

##### **Geohot** [[00:02:32](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=152)]
What's not exciting about it?

##### **Geohot** [[00:02:35](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=155)]
I don't know.

##### **Chenyu** [[00:02:35](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=155)]
Every part of it.

##### **Geohot** [[00:02:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=157)]
Why?

##### **Geohot** [[00:02:39](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=159)]
Do I have to do it?

##### **Geohot** [[00:02:40](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=160)]
Like.

##### **Geohot** [[00:02:41](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=161)]
Yeah.

##### **Geohot** [[00:02:41](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=161)]
Is that what you want me to do?

##### **Chenyu** [[00:02:44](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=164)]
Like, do you want me to start working on the training script?

##### **Geohot** [[00:02:47](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=167)]
I think it would be awesome to make a training script.

##### **Geohot** [[00:02:49](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=169)]
But, anyway, yeah.

##### **Geohot** [[00:02:50](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=170)]
Well, no.

##### **Geohot** [[00:02:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=171)]
What do you mean?

##### **Geohot** [[00:02:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=172)]
What needs to be done?

##### **Chenyu** [[00:02:53](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=173)]
Right?

##### **Geohot** [[00:02:53](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=173)]
That's the only thing I really want to do.

##### **Geohot** [[00:02:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=174)]
That's the only thing I really want to talk about in this meeting.

##### **Geohot** [[00:02:55](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=175)]
Oh.

##### **Geohot** [[00:02:57](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=177)]
Um.

##### **Geohot** [[00:02:58](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=178)]
I don't know.

##### **Chenyu** [[00:02:58](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=178)]
I mean.

##### **Geohot** [[00:02:59](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=179)]
I'm neutral.

##### **Geohot** [[00:03:00](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=180)]
I don't know what other people feel about the contract.

##### **Geohot** [[00:03:02](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=182)]
Since they get involved in the first part of getting the contract.

##### **Geohot** [[00:03:05](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=185)]
No, no, no, no, no.

##### **Geohot** [[00:03:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=186)]
Like, this company's doing the contract.

##### **Chenyu** [[00:03:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=188)]
I want everybody focused on the contract.

##### **Geohot** [[00:03:10](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=190)]
Yeah.

##### **Geohot** [[00:03:10](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=190)]
The contract is.

##### **Geohot** [[00:03:13](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=193)]
We have to succeed at this.

##### **Geohot** [[00:03:15](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=195)]
Or this is over.

##### **Geohot** [[00:03:17](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=197)]
Yeah.

##### **Chenyu** [[00:03:18](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=198)]
Like, this company's over if we don't succeed at this contract.

##### **Geohot** [[00:03:23](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=203)]
Yeah.

##### **Geohot** [[00:03:25](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=205)]
That's the part I don't want.

##### **Geohot** [[00:03:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=207)]
You don't agree with that?

##### **Geohot** [[00:03:29](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=209)]
I don't have a strong opinion.

##### **Geohot** [[00:03:30](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=210)]
No, I think if we.

##### **Chenyu** [[00:03:31](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=211)]
If we fail at this.

##### **Geohot** [[00:03:33](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=213)]
Okay.

##### **Geohot** [[00:03:33](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=213)]
Like, we said we were going to do this.

##### **Geohot** [[00:03:34](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=214)]
If we fail at this.

##### **Geohot** [[00:03:35](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=215)]
I think I'm shutting the company down.

##### **Geohot** [[00:03:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=216)]
Okay.

##### **Chenyu** [[00:03:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=217)]
Like, I think there's no point in continuing.

##### **Geohot** [[00:03:38](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=218)]
If we can't.

##### **Geohot** [[00:03:40](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=220)]
If we've come this far, we can't.

##### **Geohot** [[00:03:46](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=226)]
If we have 5 million dollars, we'll give it back to the investors.

##### **Geohot** [[00:03:48](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=228)]
There's no point if we can't do this.

##### **Geohot** [[00:03:50](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=230)]
Mm.

##### **Chenyu** [[00:03:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=231)]
Okay.

##### **Geohot** [[00:03:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=232)]
I mean.

##### **Geohot** [[00:03:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=232)]
I don't know how other people feel about it.

##### **Geohot** [[00:03:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=234)]
I don't know.

##### **Geohot** [[00:03:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=234)]
I mean, that's just from the top down.

##### **Geohot** [[00:03:55](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=235)]
If we don't succeed at this contract.

##### **Chenyu** [[00:03:58](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=238)]
Which part of that ties to a company mission?

##### **Geohot** [[00:04:03](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=243)]
What do you mean?

##### **Geohot** [[00:04:05](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=245)]
Like, no one is going to buy MI350, right?

##### **Geohot** [[00:04:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=248)]
I don't care about that.

##### **Geohot** [[00:04:10](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=250)]
If we can't succeed,

##### **Geohot** [[00:04:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=252)]
if we're so far behind the state of the art

##### **Chenyu** [[00:04:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=254)]
that we can't figure out how to get on MLPer

##### **Geohot** [[00:04:16](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=256)]
for a big LLaMA on a modern machine,

##### **Geohot** [[00:04:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=259)]
let's just throw in the towel.

##### **Geohot** [[00:04:21](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=261)]
Cool.

##### **Geohot** [[00:04:25](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=265)]
What are we missing from being able to do it?

##### **Geohot** [[00:04:29](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=269)]
Okay, it sounds like I have to do it.

##### **Chenyu** [[00:04:33](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=273)]
Try for doing it.

##### **Geohot** [[00:04:35](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=275)]
All right, so it sounds like I have to do it.

##### **Geohot** [[00:04:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=277)]
Yep.

##### **Geohot** [[00:04:38](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=278)]
All right.

##### **Geohot** [[00:04:39](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=279)]
I don't have anything else to say for the meeting then.

##### **Geohot** [[00:04:41](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=281)]
That's it.

##### **Chenyu** [[00:04:43](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=283)]
So, Quasaline, the only thing to discuss about is QTT.

##### **Geohot** [[00:04:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=291)]
So, if you will find out that

##### **Geohot** [[00:04:53](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=293)]
RockProf V3 works fine,

##### **Geohot** [[00:04:59](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=299)]
which I think I'll look into this.

##### **Geohot** [[00:05:04](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=304)]
Because currently we..

##### **Geohot** [[00:05:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=306)]
Yeah, our runtime doesn't meet any markers.

##### **Chenyu** [[00:05:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=314)]
I doubt actually..

##### **Geohot** [[00:05:15](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=315)]
RockProf doesn't even capture it.

##### **Geohot** [[00:05:21](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=321)]
Like, RockProf is used for that.

##### **Geohot** [[00:05:23](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=323)]
Yeah.

##### **Geohot** [[00:05:24](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=324)]
Yeah, you can..

##### **Geohot** [[00:05:26](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=326)]
If we can't succeed at this..

##### **Chenyu** [[00:05:28](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=328)]
You know, we're just talking about the tough line.

##### **Geohot** [[00:05:30](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=330)]
We'll talk about it on the meeting.

##### **Geohot** [[00:05:31](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=331)]
If we can't succeed at this contract..

##### **Geohot** [[00:05:34](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=334)]
Like, it's not a question of

##### **Geohot** [[00:05:35](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=335)]
if people are going to use TinyGrad to train big LLaMA.

##### **Geohot** [[00:05:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=337)]
It's a question if we're so hopelessly lost

##### **Chenyu** [[00:05:40](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=340)]
from the state of the art

##### **Geohot** [[00:05:41](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=341)]
that even with as much hand coding as we want,

##### **Geohot** [[00:05:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=345)]
we can't get this thing to train.

##### **Geohot** [[00:05:49](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=349)]
Okay.

##### **Geohot** [[00:05:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=351)]
If we can't do that,

##### **Geohot** [[00:05:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=352)]
then, like,

##### **Chenyu** [[00:05:53](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=353)]
no, I mean,

##### **Geohot** [[00:05:53](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=353)]
I have no doubt

##### **Geohot** [[00:05:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=354)]
we can do that.

##### **Geohot** [[00:05:56](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=356)]
Okay.

##### **Geohot** [[00:05:56](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=356)]
And we will do that.

##### **Geohot** [[00:05:57](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=357)]
Well, let's get paid $2 million

##### **Chenyu** [[00:05:59](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=359)]
and let's do that.

##### **Geohot** [[00:06:01](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=361)]
This is the..

##### **Geohot** [[00:06:02](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=362)]
This is the..

##### **Geohot** [[00:06:03](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=363)]
This is the..

##### **Geohot** [[00:06:03](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=363)]
This is..

##### **Geohot** [[00:06:03](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=363)]
There's $1.6 million on the table

##### **Chenyu** [[00:06:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=366)]
of pure profit.

##### **Geohot** [[00:06:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=368)]
Okay.

##### **Geohot** [[00:06:10](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=370)]
Right?

##### **Geohot** [[00:06:11](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=371)]
Like..

##### **Geohot** [[00:06:11](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=371)]
I don't know.

##### **Geohot** [[00:06:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=372)]
I'm not motivated by $1.6 million.

##### **Chenyu** [[00:06:15](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=375)]
It's not about the money, though.

##### **Geohot** [[00:06:16](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=376)]
It's about, like, the, like..

##### **Geohot** [[00:06:18](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=378)]
What's it about?

##### **Geohot** [[00:06:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=379)]
What?

##### **Geohot** [[00:06:20](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=380)]
So, I already know

##### **Geohot** [[00:06:22](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=382)]
if we spend time..

##### **Chenyu** [[00:06:23](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=383)]
to handwrite these kernels,

##### **Geohot** [[00:06:25](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=385)]
we are able to go into

##### **Geohot** [[00:06:26](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=386)]
channel model

##### **Geohot** [[00:06:26](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=386)]
on the..

##### **Geohot** [[00:06:28](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=388)]
Yeah, let's do it.

##### **Geohot** [[00:06:30](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=390)]
No.

##### **Chenyu** [[00:06:31](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=391)]
Well, but..

##### **Geohot** [[00:06:32](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=392)]
What do you mean?

##### **Geohot** [[00:06:34](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=394)]
What's the part

##### **Geohot** [[00:06:34](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=394)]
that's exciting about this?

##### **Geohot** [[00:06:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=396)]
You already know

##### **Geohot** [[00:06:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=397)]
we can do it.

##### **Chenyu** [[00:06:39](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=399)]
But..

##### **Geohot** [[00:06:39](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=399)]
No, I don't.

##### **Geohot** [[00:06:41](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=401)]
And, like,

##### **Geohot** [[00:06:42](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=402)]
I don't see any better way

##### **Geohot** [[00:06:43](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=403)]
to push TinyGrad forward

##### **Geohot** [[00:06:44](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=404)]
than to actually try to do this.

##### **Chenyu** [[00:06:46](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=406)]
Yeah, maybe that's the problem.

##### **Geohot** [[00:06:48](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=408)]
What do you mean?

##### **Geohot** [[00:06:49](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=409)]
You think there's a better way?

##### **Geohot** [[00:06:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=411)]
I don't know.

##### **Geohot** [[00:06:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=412)]
I really don't think so.

##### **Geohot** [[00:06:53](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=413)]
Okay.

##### **Chenyu** [[00:06:55](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=415)]
Like, again,

##### **Geohot** [[00:06:56](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=416)]
this is what everyone..

##### **Geohot** [[00:06:58](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=418)]
This is what Chris Lattner said to us.

##### **Geohot** [[00:06:59](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=419)]
He's like,

##### **Geohot** [[00:07:00](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=420)]
I want to see speed

##### **Geohot** [[00:07:01](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=421)]
from your thing.

##### **Chenyu** [[00:07:03](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=423)]
TinyGrad is hopelessly slow.

##### **Geohot** [[00:07:05](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=425)]
Yes.

##### **Geohot** [[00:07:05](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=425)]
That's the main problem with it.

##### **Geohot** [[00:07:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=427)]
Yeah.

##### **Geohot** [[00:07:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=427)]
When he said that,

##### **Geohot** [[00:07:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=428)]
he doesn't mean, like,

##### **Chenyu** [[00:07:10](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=430)]
see how good you can

##### **Geohot** [[00:07:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=432)]
handwrite these kernels, right?

##### **Geohot** [[00:07:13](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=433)]
He does.

##### **Geohot** [[00:07:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=434)]
Oh, he does.

##### **Geohot** [[00:07:15](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=435)]
And this is what Mojo is.

##### **Geohot** [[00:07:17](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=437)]
Okay.

##### **Chenyu** [[00:07:17](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=437)]
He didn't write an AI compiler.

##### **Geohot** [[00:07:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=439)]
He says it's impossible.

##### **Geohot** [[00:07:20](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=440)]
The greatest compiler guy

##### **Geohot** [[00:07:21](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=441)]
in the world

##### **Geohot** [[00:07:22](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=442)]
says,

##### **Geohot** [[00:07:22](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=442)]
you can't write an AI compiler.

##### **Chenyu** [[00:07:24](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=444)]
Okay.

##### **Geohot** [[00:07:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=447)]
That's an issue, right?

##### **Geohot** [[00:07:28](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=448)]
So, if we believe in that,

##### **Geohot** [[00:07:30](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=450)]
then maybe there's no point

##### **Geohot** [[00:07:31](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=451)]
for TinyGrad.

##### **Geohot** [[00:07:32](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=452)]
Maybe we already lost to Mojo.

##### **Chenyu** [[00:07:34](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=454)]
How can we beat Mojo?

##### **Geohot** [[00:07:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=456)]
In a lot of ways.

##### **Geohot** [[00:07:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=457)]
And it's not that

##### **Geohot** [[00:07:38](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=458)]
we can't beat Mojo.

##### **Geohot** [[00:07:39](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=459)]
It's about the timelines.

##### **Geohot** [[00:07:40](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=460)]
The same as Tesla.

##### **Chenyu** [[00:07:41](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=461)]
It's the same as Kama and Tesla, right?

##### **Geohot** [[00:07:43](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=463)]
It's not..

##### **Geohot** [[00:07:44](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=464)]
You know, if we look back,

##### **Geohot** [[00:07:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=465)]
and at Kama,

##### **Geohot** [[00:07:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=465)]
we were talking about

##### **Geohot** [[00:07:46](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=466)]
building driving simulators

##### **Chenyu** [[00:07:48](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=468)]
right at the beginning of the company.

##### **Geohot** [[00:07:50](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=470)]
But the technology

##### **Geohot** [[00:07:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=471)]
just hopelessly

##### **Geohot** [[00:07:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=472)]
wasn't there.

##### **Geohot** [[00:07:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=472)]
You look at the original

##### **Geohot** [[00:07:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=474)]
learning and driving simulator paper,

##### **Chenyu** [[00:07:55](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=475)]
and all you see is

##### **Geohot** [[00:08:00](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=480)]
like

##### **Geohot** [[00:08:02](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=482)]
little grainy images.

##### **Geohot** [[00:08:04](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=484)]
And it's not that

##### **Geohot** [[00:08:05](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=485)]
we got any better

##### **Geohot** [[00:08:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=486)]
at data collection

##### **Chenyu** [[00:08:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=487)]
or training or anything.

##### **Geohot** [[00:08:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=488)]
We just waited

##### **Geohot** [[00:08:09](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=489)]
for the state of the art

##### **Geohot** [[00:08:10](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=490)]
to improve.

##### **Geohot** [[00:08:11](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=491)]
The same strategy,

##### **Geohot** [[00:08:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=492)]
I think, applies here.

##### **Chenyu** [[00:08:13](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=493)]
No, but here,

##### **Geohot** [[00:08:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=494)]
we already know

##### **Geohot** [[00:08:15](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=495)]
what the state of the art is.

##### **Geohot** [[00:08:16](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=496)]
No.

##### **Geohot** [[00:08:17](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=497)]
Are we going to write

##### **Geohot** [[00:08:18](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=498)]
better kernels

##### **Chenyu** [[00:08:18](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=498)]
than what people are writing now?

##### **Geohot** [[00:08:20](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=500)]
That doesn't matter.

##### **Geohot** [[00:08:21](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=501)]
We're going to write

##### **Geohot** [[00:08:21](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=501)]
simpler.

##### **Geohot** [[00:08:22](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=502)]
We're going to write something

##### **Geohot** [[00:08:23](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=503)]
that's actually

##### **Chenyu** [[00:08:23](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=503)]
machine searchable.

##### **Geohot** [[00:08:29](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=509)]
Okay.

##### **Geohot** [[00:08:30](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=510)]
But like,

##### **Geohot** [[00:08:31](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=511)]
how are we supposed to know

##### **Geohot** [[00:08:33](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=513)]
on what areas to push

##### **Geohot** [[00:08:35](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=515)]
if we don't have

##### **Chenyu** [[00:08:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=516)]
any state of the art

##### **Geohot** [[00:08:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=516)]
kernels in TinyRack?

##### **Geohot** [[00:08:44](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=524)]
On accounts?

##### **Geohot** [[00:08:48](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=528)]
Right.

##### **Geohot** [[00:08:48](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=528)]
Like,

##### **Geohot** [[00:08:49](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=529)]
we committed

##### **Chenyu** [[00:08:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=531)]
to this contract.

##### **Geohot** [[00:08:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=532)]
We have to do this contract.

##### **Geohot** [[00:08:53](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=533)]
And the only way

##### **Geohot** [[00:08:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=534)]
I would consider

##### **Geohot** [[00:08:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=534)]
focusing on anything else

##### **Geohot** [[00:08:55](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=535)]
is if someone else

##### **Chenyu** [[00:08:56](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=536)]
was offering us more money.

##### **Geohot** [[00:08:57](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=537)]
And it's not about the money.

##### **Geohot** [[00:08:59](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=539)]
It's about it's worth

##### **Geohot** [[00:09:00](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=540)]
$1.6 million

##### **Geohot** [[00:09:01](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=541)]
to somebody else.

##### **Geohot** [[00:09:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=546)]
It's low.

##### **Chenyu** [[00:09:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=547)]
Yeah.

##### **Geohot** [[00:09:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=547)]
Why?

##### **Geohot** [[00:09:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=548)]
I don't think it is.

##### **Geohot** [[00:09:10](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=550)]
Why did they give us the money?

##### **Geohot** [[00:09:13](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=553)]
For other reasons.

##### **Geohot** [[00:09:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=554)]
Like what?

##### **Chenyu** [[00:09:15](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=555)]
Like the potential bugs

##### **Geohot** [[00:09:16](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=556)]
or the things we can find

##### **Geohot** [[00:09:17](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=557)]
to help them.

##### **Geohot** [[00:09:20](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=560)]
What do you mean?

##### **Geohot** [[00:09:23](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=563)]
It's not clear

##### **Geohot** [[00:09:24](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=564)]
this task is worth

##### **Chenyu** [[00:09:25](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=565)]
$1.6 million to them.

##### **Geohot** [[00:09:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=567)]
It's easily worth

##### **Geohot** [[00:09:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=567)]
$1.6 million to them.

##### **Geohot** [[00:09:29](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=569)]
Yeah.

##### **Geohot** [[00:09:29](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=569)]
I mean,

##### **Geohot** [[00:09:30](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=570)]
maybe that's the difference, right?

##### **Chenyu** [[00:09:31](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=571)]
You believe so.

##### **Geohot** [[00:09:32](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=572)]
So you have the drive.

##### **Geohot** [[00:09:33](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=573)]
Wait, wait, wait, wait, wait.

##### **Geohot** [[00:09:34](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=574)]
What?

##### **Geohot** [[00:09:34](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=574)]
You think I bullied them into it?

##### **Geohot** [[00:09:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=576)]
You think somehow, like,

##### **Chenyu** [[00:09:38](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=578)]
no.

##### **Geohot** [[00:09:39](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=579)]
They were more,

##### **Geohot** [[00:09:40](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=580)]
this is more like

##### **Geohot** [[00:09:41](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=581)]
their marketing or developer

##### **Geohot** [[00:09:44](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=584)]
advocate fault, right?

##### **Geohot** [[00:09:46](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=586)]
Well, yeah, but of course,

##### **Chenyu** [[00:09:47](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=587)]
the goal,

##### **Geohot** [[00:09:47](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=587)]
I'm not saying that the $1.6 million

##### **Geohot** [[00:09:49](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=589)]
is literally because

##### **Geohot** [[00:09:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=591)]
TinyGrad can train a LLaMA.

##### **Geohot** [[00:09:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=592)]
Of course not.

##### **Geohot** [[00:09:53](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=593)]
Okay.

##### **Chenyu** [[00:09:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=594)]
But why would you not want to fund

##### **Geohot** [[00:09:58](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=598)]
alternative approaches?

##### **Geohot** [[00:09:58](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=598)]
Of course you do.

##### **Geohot** [[00:09:59](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=599)]
Yeah, of course you do.

##### **Geohot** [[00:10:00](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=600)]
But that doesn't mean

##### **Geohot** [[00:10:01](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=601)]
it's worth that money to you.

##### **Chenyu** [[00:10:03](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=603)]
That's more like a hedge.

##### **Geohot** [[00:10:05](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=605)]
No, it's worth that money.

##### **Geohot** [[00:10:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=606)]
If we succeed at this,

##### **Geohot** [[00:10:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=607)]
it's worth that money to them.

##### **Geohot** [[00:10:09](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=609)]
Wait, you really don't believe that?

##### **Geohot** [[00:10:11](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=611)]
No.

##### **Chenyu** [[00:10:13](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=613)]
Why?

##### **Geohot** [[00:10:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=614)]
If I had hardware,

##### **Geohot** [[00:10:15](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=615)]
if I had a hardware company

##### **Geohot** [[00:10:17](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=617)]
and I could pay someone $1.6 million

##### **Geohot** [[00:10:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=619)]
to build an alternative stack

##### **Geohot** [[00:10:21](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=621)]
that succeeds at training

##### **Chenyu** [[00:10:22](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=622)]
the state of the art on my hardware,

##### **Geohot** [[00:10:25](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=625)]
I'd pay that in a minute.

##### **Geohot** [[00:10:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=627)]
Okay.

##### **Geohot** [[00:10:28](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=628)]
I'm not doubting you believing that,

##### **Geohot** [[00:10:30](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=630)]
but just I don't believe in that.

##### **Geohot** [[00:10:32](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=632)]
But what do you mean?

##### **Chenyu** [[00:10:33](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=633)]
The tape out of that chip is $150 million.

##### **Geohot** [[00:10:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=636)]
Yes.

##### **Geohot** [[00:10:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=637)]
If you paid $150 million for taping,

##### **Geohot** [[00:10:39](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=639)]
why would you not put $50 million

##### **Geohot** [[00:10:41](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=641)]
scattered randomly into software?

##### **Geohot** [[00:10:46](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=646)]
Oh, maybe later.

##### **Chenyu** [[00:10:47](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=647)]
Yeah.

##### **Geohot** [[00:10:49](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=649)]
Then why would you not want these software projects

##### **Geohot** [[00:10:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=651)]
to succeed at exactly that goal?

##### **Geohot** [[00:10:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=652)]
I think it's a smart..

##### **Geohot** [[00:10:53](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=653)]
So you think it's a dumb goal.

##### **Geohot** [[00:10:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=654)]
You think that AMD should have asked for something else

##### **Chenyu** [[00:10:56](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=656)]
or you think there's nothing we can provide to AMD

##### **Geohot** [[00:10:58](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=658)]
that has value?

##### **Geohot** [[00:10:59](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=659)]
It's not clear what we are doing provides value to them,

##### **Geohot** [[00:11:04](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=664)]
at least to me.

##### **Geohot** [[00:11:05](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=665)]
Why?

##### **Geohot** [[00:11:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=666)]
It's just not clear to me.

##### **Chenyu** [[00:11:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=668)]
Maybe I'm just not educated.

##### **Geohot** [[00:11:09](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=669)]
I don't know.

##### **Geohot** [[00:11:11](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=671)]
Well, but okay, so..

##### **Geohot** [[00:11:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=672)]
Because you're Starless,

##### **Geohot** [[00:11:13](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=673)]
you have the most of the communication with them, right?

##### **Geohot** [[00:11:16](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=676)]
So maybe you know better.

##### **Chenyu** [[00:11:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=679)]
No, I mean, look..

##### **Geohot** [[00:11:21](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=681)]
I mean, look, I know like part of it already.

##### **Geohot** [[00:11:24](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=684)]
That's because I'm in the office and talk to you on this,

##### **Geohot** [[00:11:26](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=686)]
like what other people think I don't even know.

##### **Geohot** [[00:11:30](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=690)]
Well..

##### **Geohot** [[00:11:35](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=695)]
I mean, again, so okay, you think..

##### **Chenyu** [[00:11:38](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=698)]
I think this is a good challenge,

##### **Geohot** [[00:11:40](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=700)]
and I think we'll be able to do it.

##### **Geohot** [[00:11:42](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=702)]
I would like take the training around.

##### **Geohot** [[00:11:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=705)]
It's like whatever days they'll probably be done.

##### **Geohot** [[00:11:47](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=707)]
I think it's a good challenge.

##### **Geohot** [[00:11:47](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=707)]
At the end of this CS,

##### **Chenyu** [[00:11:49](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=709)]
but I don't quite see what's the difference for the company.

##### **Geohot** [[00:11:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=712)]
Like what do we do after that and things like that.

##### **Geohot** [[00:11:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=714)]
What do we do after that?

##### **Geohot** [[00:11:55](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=715)]
We figure out how to do that and make it easy.

##### **Geohot** [[00:11:57](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=717)]
Okay.

##### **Geohot** [[00:11:58](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=718)]
We figure out what we didn't do for the DSP contract

##### **Chenyu** [[00:12:00](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=720)]
because there's no real market for using Titan.

##### **Geohot** [[00:12:02](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=722)]
There's no real market at all on these DSPs.

##### **Geohot** [[00:12:04](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=724)]
No one uses them.

##### **Geohot** [[00:12:05](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=725)]
But a ton of people use MI355X.

##### **Geohot** [[00:12:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=728)]
And they will use TitanGrip?

##### **Geohot** [[00:12:10](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=730)]
Probably, yeah.

##### **Chenyu** [[00:12:11](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=731)]
Is that our direction?

##### **Geohot** [[00:12:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=732)]
Yeah.

##### **Geohot** [[00:12:13](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=733)]
Okay.

##### **Geohot** [[00:12:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=734)]
I don't quite see that, but..

##### **Geohot** [[00:12:16](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=736)]
What do you think they're going to use?

##### **Geohot** [[00:12:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=739)]
Jaxx.

##### **Chenyu** [[00:12:20](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=740)]
With the MI355X?

##### **Geohot** [[00:12:21](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=741)]
Yeah.

##### **Geohot** [[00:12:22](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=742)]
Have you tried it?

##### **Geohot** [[00:12:23](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=743)]
No.

##### **Geohot** [[00:12:24](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=744)]
Yeah, it doesn't work.

##### **Geohot** [[00:12:25](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=745)]
Yeah, but..

##### **Chenyu** [[00:12:26](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=746)]
Similar to TinyGrid doesn't work today.

##### **Geohot** [[00:12:28](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=748)]
No, TinyGrid works better.

##### **Geohot** [[00:12:30](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=750)]
I don't think Jaxx works at all.

##### **Geohot** [[00:12:33](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=753)]
Yeah.

##### **Geohot** [[00:12:35](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=755)]
Their GPU thing in Jaxx is way worse already.

##### **Geohot** [[00:12:39](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=759)]
And you know if anyone put any effort into it, it's on Nvidia.

##### **Chenyu** [[00:12:43](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=763)]
Yeah, maybe.

##### **Geohot** [[00:12:44](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=764)]
The GPU backend on Jaxx just kind of isn't there.

##### **Geohot** [[00:12:46](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=766)]
Jaxx is an advertiser.

##### **Geohot** [[00:12:47](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=767)]
It's not for TPUs.

##### **Geohot** [[00:12:48](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=768)]
The Jaxx backend is very good on TPUs.

##### **Geohot** [[00:12:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=771)]
Or just handwrite these kernels, right?

##### **Chenyu** [[00:12:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=774)]
What do you mean?

##### **Geohot** [[00:12:55](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=775)]
If you're going to do a big training around, it's just handwritten kernels.

##### **Geohot** [[00:12:58](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=778)]
Yeah, but what about all the people in the middle?

##### **Geohot** [[00:13:02](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=782)]
Who are the people in the middle?

##### **Geohot** [[00:13:04](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=784)]
Who is going to use something in the middle?

##### **Geohot** [[00:13:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=787)]
Every researcher.

##### **Chenyu** [[00:13:09](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=789)]
Is Comma going to use TinyGrid to train?

##### **Geohot** [[00:13:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=792)]
Not soon.

##### **Geohot** [[00:13:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=794)]
Because they're on Nvidia.

##### **Geohot** [[00:13:15](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=795)]
But if Comma was forced to use AMD hardware, yeah.

##### **Geohot** [[00:13:17](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=797)]
So you think if we do this contract, Comma would be more willing to use TinyGrid for their training?

##### **Geohot** [[00:13:24](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=804)]
No, I don't think they want AMD hardware.

##### **Chenyu** [[00:13:26](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=806)]
I think if we..

##### **Geohot** [[00:13:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=807)]
Okay, if Comma is not really using..

##### **Geohot** [[00:13:30](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=810)]
Who are these users we are talking about that potentially would use TinyGrid for training?

##### **Geohot** [[00:13:34](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=814)]
What do you mean?

##### **Geohot** [[00:13:35](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=815)]
Every..

##### **Geohot** [[00:13:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=816)]
Again, like, why does anyone buy AMD hardware, right?

##### **Chenyu** [[00:13:38](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=818)]
People are buying it, right?

##### **Geohot** [[00:13:41](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=821)]
Yes.

##### **Geohot** [[00:13:42](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=822)]
Very little amount of people.

##### **Geohot** [[00:13:44](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=824)]
Very little amount of people.

##### **Geohot** [[00:13:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=825)]
Look at AMD stock.

##### **Geohot** [[00:13:49](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=829)]
Oh, it has nothing to do with the sales.

##### **Chenyu** [[00:13:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=831)]
No, it does.

##### **Geohot** [[00:13:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=832)]
It absolutely does.

##### **Geohot** [[00:13:53](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=833)]
AMD sells are way up.

##### **Geohot** [[00:13:56](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=836)]
Way up and still tiny, right?

##### **Geohot** [[00:13:58](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=838)]
I mean..

##### **Geohot** [[00:13:59](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=839)]
If Comma is not..

##### **Chenyu** [[00:14:00](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=840)]
What do you mean by tiny?

##### **Geohot** [[00:14:01](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=841)]
You want to compare it to TenStore and Grok?

##### **Geohot** [[00:14:05](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=845)]
Grok has users.

##### **Geohot** [[00:14:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=846)]
Buys their hardware while they have users.

##### **Geohot** [[00:14:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=848)]
That's different.

##### **Geohot** [[00:14:10](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=850)]
I have a lot of questions about whether Grok actually has users.

##### **Chenyu** [[00:14:13](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=853)]
Yeah, I don't know.

##### **Geohot** [[00:14:13](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=853)]
I think they lose money on each other.

##### **Geohot** [[00:14:15](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=855)]
My point is..

##### **Geohot** [[00:14:18](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=858)]
Do we really have users who will be willing to use TinyGrid for training LLaMA or anything

##### **Geohot** [[00:14:26](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=866)]
like that?

##### **Geohot** [[00:14:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=867)]
Yeah, but it's not like training LLaMA is some crazy task that..

##### **Chenyu** [[00:14:30](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=870)]
Yeah, that's what I mean.

##### **Geohot** [[00:14:31](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=871)]
Because it's not a crazy task.

##### **Geohot** [[00:14:33](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=873)]
You just can write 10 kernels or people already write it for you on the board.

##### **Geohot** [[00:14:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=877)]
Yeah, well, let's get those 10 kernels handwritten and show that TinyGrid can get performance

##### **Geohot** [[00:14:41](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=881)]
like that.

##### **Geohot** [[00:14:42](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=882)]
Can you come up with a better task?

##### **Chenyu** [[00:14:46](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=886)]
Maybe not.

##### **Geohot** [[00:14:46](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=886)]
That's what I'm saying.

##### **Geohot** [[00:14:47](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=887)]
That's what I mean.

##### **Geohot** [[00:14:48](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=888)]
And we're getting paid $1.6 million for this task.

##### **Geohot** [[00:14:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=894)]
Yeah.

##### **Geohot** [[00:14:56](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=896)]
I don't know.

##### **Chenyu** [[00:15:03](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=903)]
Like, okay, if no one else wants to do this, I'll do it.

##### **Geohot** [[00:15:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=906)]
Yeah, I'll do it, but I'll do it probably similar to previous MLPerf.

##### **Geohot** [[00:15:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=912)]
What do you mean?

##### **Geohot** [[00:15:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=914)]
It's like, does the previous MLPerf give us anything?

##### **Geohot** [[00:15:17](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=917)]
Yes.

##### **Geohot** [[00:15:18](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=918)]
Like what?

##### **Chenyu** [[00:15:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=919)]
I mean, that was a great direction.

##### **Geohot** [[00:15:23](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=923)]
That got us building out, like we fixed so many bugs.

##### **Geohot** [[00:15:28](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=928)]
Yes.

##### **Geohot** [[00:15:30](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=930)]
It didn't get us speed, but it got us the whole front end.

##### **Geohot** [[00:15:34](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=934)]
The whole front end, all the stability of gradient and stuff.

##### **Geohot** [[00:15:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=937)]
But that all came from the previous MLPerf.

##### **Chenyu** [[00:15:40](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=940)]
Maybe it comes from the first tier.

##### **Geohot** [[00:15:42](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=942)]
But what about the one next?

##### **Geohot** [[00:15:44](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=944)]
Which one next?

##### **Geohot** [[00:15:46](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=946)]
So we have ResNet.

##### **Geohot** [[00:15:47](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=947)]
Two years ago.

##### **Geohot** [[00:15:49](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=949)]
Yeah.

##### **Chenyu** [[00:15:49](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=949)]
Okay.

##### **Geohot** [[00:15:50](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=950)]
And we got BERT a little after.

##### **Geohot** [[00:15:53](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=953)]
Sounds good.

##### **Geohot** [[00:15:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=954)]
Okay.

##### **Geohot** [[00:15:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=954)]
What about the two after?

##### **Geohot** [[00:15:56](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=956)]
Did we even submit?

##### **Chenyu** [[00:15:57](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=957)]
I think we did speed ups for one of the BERTs, but no, I don't think they were that.

##### **Geohot** [[00:16:02](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=962)]
No, I don't think you're telling me that's wrong.

##### **Geohot** [[00:16:04](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=964)]
No, I think that it was important to get ResNet and BERT.

##### **Geohot** [[00:16:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=967)]
But yeah, I think, I mean, we have to go back to succeeding in MLPerf and we have to start

##### **Geohot** [[00:16:10](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=970)]
getting good times.

##### **Geohot** [[00:16:15](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=975)]
What else is there to do?

##### **Chenyu** [[00:16:18](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=978)]
That's a great question.

##### **Geohot** [[00:16:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=979)]
I don't know.

##### **Geohot** [[00:16:20](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=980)]
But it also feels weird that the only thing that possibly can help people is doing MLPerf

##### **Geohot** [[00:16:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=987)]
training around.

##### **Geohot** [[00:16:28](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=988)]
But it is.

##### **Geohot** [[00:16:29](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=989)]
It's just not fast enough yet.

##### **Chenyu** [[00:16:31](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=991)]
Yes.

##### **Geohot** [[00:16:32](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=992)]
Okay.

##### **Geohot** [[00:16:34](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=994)]
What else is there to this?

##### **Geohot** [[00:16:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=996)]
Multiple.

##### **Geohot** [[00:16:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=997)]
I mean, I don't know, right?

##### **Geohot** [[00:16:38](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=998)]
I retweeted two people last week who were like, TinyGrad is way better to use than PyTorch.

##### **Chenyu** [[00:16:43](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1003)]
It's just slow.

##### **Geohot** [[00:16:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1005)]
I mean, I don't know.

##### **Geohot** [[00:16:46](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1006)]
I mean, I don't know.

##### **Geohot** [[00:16:46](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1006)]
I mean, I don't know.

##### **Geohot** [[00:16:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1011)]
I mean, I don't know.

##### **Geohot** [[00:16:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1012)]
I'm just getting used to it.

##### **Chenyu** [[00:16:53](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1013)]
But, yeah.

##### **Geohot** [[00:16:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1014)]
I mean, I think, yeah.

##### **Geohot** [[00:16:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1014)]
It's just, it's just bad.

##### **Geohot** [[00:16:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1014)]
I think it's good to be able to use it for, you know, for research.

##### **Geohot** [[00:16:57](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1017)]
Yeah, I saw a show there.

##### **Geohot** [[00:16:59](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1019)]
I bet they even use it for weirder training than PyTorch.

##### **Chenyu** [[00:17:04](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1024)]
The goal also is not like, like if we do this in such a way, it'll work for everything

##### **Geohot** [[00:17:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1032)]
that's kind of like LLaMA too it's not just long oh sure i mean yes you got a similar transformer

##### **Geohot** [[00:17:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1039)]
stuff or attention stuff but not just the transformer and attention stuff right like

##### **Geohot** [[00:17:23](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1043)]
the play else well it's not like we're gonna it's not like we're handwriting kernels in hip

##### **Geohot** [[00:17:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1047)]
right i'm not proposing that oh sure we can write kernels in uop yeah okay okay but i mean do you

##### **Geohot** [[00:17:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1057)]
see why i'm pushing for that because i don't know how to improve the search uh i don't understand

##### **Chenyu** [[00:17:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1065)]
yes okay so what better thing to do then instead of to make up some contrived kernels do the

##### **Geohot** [[00:17:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1071)]
kernels that they're paying us 1.6 million dollars for this one maybe it's funny this is

##### **Geohot** [[00:18:03](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1083)]
this contract's the best thing ever to come to this company

##### **Geohot** [[00:18:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1086)]
oh that i agree

##### **Geohot** [[00:18:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1087)]
okay then let's complete it if we fail at it the company's over

##### **Geohot** [[00:18:15](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1095)]
that's all i'm not supposed to be what do you mean i mean look i'm not here to i'm not here

##### **Chenyu** [[00:18:21](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1101)]
to motivate you right like this is what we're doing right you can stay with this company and

##### **Geohot** [[00:18:25](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1105)]
do this or not right that's just how it is yeah cool um yeah

##### **Geohot** [[00:18:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1116)]
okay

##### **Geohot** [[00:18:42](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1122)]
so so

##### **Geohot** [[00:18:43](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1123)]
i'm going to just like slowly run through some your questions

##### **Geohot** [[00:18:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1125)]
getting this después

##### **Chenyu** [[00:18:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1125)]
contract should quit today. Think about whether you're motivated to work on it. And then also,

##### **Geohot** [[00:18:50](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1130)]
let's figure out what everyone knows how to do. And then whatever anyone doesn't know how to do,

##### **Geohot** [[00:18:55](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1135)]
I'll do. Okay, I'll do this whole thing myself if I have to. I'd rather not.

##### **Geohot** [[00:19:05](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1145)]
Yeah, I mean, I've taken an approach where I think I can get the DSP contract mostly myself.

##### **Geohot** [[00:19:10](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1150)]
That's another thing. What do we get from the DSP contract?

##### **Geohot** [[00:19:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1154)]
The entire devectorizer and expander stack.

##### **Chenyu** [[00:19:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1159)]
Okay. What has that changed?

##### **Geohot** [[00:19:24](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1164)]
What has the devectorizer and the expander changed?

##### **Geohot** [[00:19:26](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1166)]
Yes.

##### **Geohot** [[00:19:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1167)]
Like it supports things that are just like, the old one was hand-coated garbage.

##### **Geohot** [[00:19:35](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1175)]
The old ones were hand-coated float4 everywhere.

##### **Geohot** [[00:19:38](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1178)]
Okay.

##### **Chenyu** [[00:19:39](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1179)]
It forced us to genericize to 128.

##### **Geohot** [[00:19:44](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1184)]
Now things like upcasted warps are possible.

##### **Geohot** [[00:19:53](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1193)]
I mean, again, I'm open to a different proposal, but I need a concrete proposal.

##### **Geohot** [[00:19:58](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1198)]
Yeah, I'm thinking about it.

##### **Geohot** [[00:19:59](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1199)]
So I cannot think of it right now.

##### **Geohot** [[00:20:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1206)]
Okay, maybe other people should talk.

##### **Chenyu** [[00:20:21](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1221)]
Other people, are you excited about the contract?

##### **Geohot** [[00:20:30](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1230)]
I am.

##### **Geohot** [[00:20:33](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1233)]
Yeah.

##### **Geohot** [[00:20:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1237)]
Yeah.

##### **Geohot** [[00:20:42](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1242)]
I mean, it's the first step, right?

##### **Geohot** [[00:20:44](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1244)]
If we can't do this,

##### **Chenyu** [[00:20:48](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1248)]
search can never accomplish it either.

##### **Geohot** [[00:20:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1254)]
Yeah, I mean, that's kind of my takeaway too, right?

##### **Geohot** [[00:20:58](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1258)]
It's not like there is any reason to like, look, I don't care how long this is going to take.

##### **Geohot** [[00:21:03](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1263)]
This is going to work.

##### **Geohot** [[00:21:04](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1264)]
I don't care if it takes six months.

##### **Geohot** [[00:21:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1267)]
I don't care if it takes five years.

##### **Chenyu** [[00:21:09](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1269)]
I don't care if it takes six months.

##### **Geohot** [[00:21:09](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1269)]
I don't care if it takes 20.

##### **Geohot** [[00:21:10](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1270)]
This is going to work.

##### **Geohot** [[00:21:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1272)]
It has to.

##### **Geohot** [[00:21:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1274)]
It's the same thing with end-to-end.

##### **Geohot** [[00:21:16](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1276)]
It's the exact same thing with self-driving cars, right?

##### **Chenyu** [[00:21:18](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1278)]
Like, look, now Tesla is saying end-to-end.

##### **Geohot** [[00:21:20](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1280)]
Waymo is saying end-to-end.

##### **Geohot** [[00:21:21](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1281)]
Everyone is saying end-to-end.

##### **Geohot** [[00:21:22](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1282)]
I said it 10 years ago, and I was like, this is going to work.

##### **Geohot** [[00:21:25](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1285)]
Is it going to work in six months?

##### **Geohot** [[00:21:26](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1286)]
No.

##### **Chenyu** [[00:21:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1287)]
Of course not.

##### **Geohot** [[00:21:28](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1288)]
I have no idea how long it's going to take, but it's obviously the right approach.

##### **Geohot** [[00:21:30](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1290)]
This is obviously the right approach to software.

##### **Geohot** [[00:21:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1296)]
I don't know.

##### **Geohot** [[00:21:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1296)]
Like, there's going to be..

##### **Geohot** [[00:21:39](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1299)]
You know, you're going to do things along the way that look stupid, right?

##### **Chenyu** [[00:21:42](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1302)]
That was brought up at Comic-Con, right?

##### **Geohot** [[00:21:44](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1304)]
Like, a lot of, like, things you do along the way look stupid.

##### **Geohot** [[00:21:46](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1306)]
But it's not like you can do it better, right?

##### **Geohot** [[00:21:48](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1308)]
You just got to accept that.

##### **Geohot** [[00:21:50](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1310)]
And you just keep working on it, and that's it.

##### **Geohot** [[00:22:05](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1325)]
Like, fundamentally, at the end of the day, this wins.

##### **Chenyu** [[00:22:10](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1330)]
Porsche definitely doesn't win.

##### **Geohot** [[00:22:16](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1336)]
I think Mojo carves out a non-AI niche.

##### **Geohot** [[00:22:20](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1340)]
Or things that just can't be expressed in the tiny grad language.

##### **Geohot** [[00:22:24](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1344)]
I think Jax does well, but I think we're really using a lot of the same ideas as they are.

##### **Geohot** [[00:22:31](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1351)]
And I think Jax, again, is mostly an ad for TPUs.

##### **Geohot** [[00:22:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1357)]
So, yeah.

##### **Chenyu** [[00:22:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1357)]
I mean, of course, like..

##### **Geohot** [[00:22:39](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1359)]
Like, if Google wasn't thinking..

##### **Geohot** [[00:22:41](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1361)]
Like, Google's thinking in the exact same way, but as what always happens with these things.

##### **Geohot** [[00:22:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1365)]
Google's infrastructure is multiple years ahead of the rest of the world,

##### **Geohot** [[00:22:48](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1368)]
but they somehow completely fumble the ball at shipping it,

##### **Geohot** [[00:22:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1371)]
which is exactly what will happen here.

##### **Chenyu** [[00:22:53](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1373)]
And then the open source one actually is the one that gets all the adoption.

##### **Geohot** [[00:23:02](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1382)]
Like, yeah.

##### **Geohot** [[00:23:03](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1383)]
Like, we got to, you know, we got to take all the ideas from..

##### **Geohot** [[00:23:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1387)]
You know, the good ideas from, like..

##### **Geohot** [[00:23:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1388)]
Like, there's a lot of..

##### **Geohot** [[00:23:09](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1389)]
There's a lot of smart people in this space.

##### **Chenyu** [[00:23:11](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1391)]
Jax, TVM, Mojo, PyTorch, they're written by very smart people.

##### **Geohot** [[00:23:15](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1395)]
And we got to take the best ideas from them.

##### **Geohot** [[00:23:17](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1397)]
But then you do it and you keep the whole thing simple.

##### **Geohot** [[00:23:21](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1401)]
These people end up with every, you know, thing.

##### **Geohot** [[00:23:25](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1405)]
It's just like..

##### **Geohot** [[00:23:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1407)]
Sure, you can write this with 10,000 lines of hacks, or you could not.

##### **Chenyu** [[00:23:31](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1411)]
Right?

##### **Geohot** [[00:23:31](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1411)]
Now, you can say, like, I don't want to handle code kernels.

##### **Geohot** [[00:23:33](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1413)]
We should just focus on search.

##### **Geohot** [[00:23:35](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1415)]
We should just not handle code kernels.

##### **Geohot** [[00:23:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1416)]
Like, that's an approach.

##### **Geohot** [[00:23:38](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1418)]
There's two problems.

##### **Chenyu** [[00:23:39](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1419)]
One, if we do that, we're not going to finish the contract in time.

##### **Geohot** [[00:23:43](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1423)]
There's no way we're going to find that flash attention online max.

##### **Geohot** [[00:23:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1431)]
The rules to search for that will be..

##### **Geohot** [[00:23:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1434)]
You know, again, I think we can have them in a year,

##### **Geohot** [[00:23:57](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1437)]
but I don't think we can have them in three months.

##### **Geohot** [[00:24:00](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1440)]
The second thing is I wish I'd spent more time hand coding kernels

##### **Chenyu** [[00:24:05](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1445)]
before I worked on search the first time.

##### **Geohot** [[00:24:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1447)]
Right?

##### **Geohot** [[00:24:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1448)]
Or I wish I'd read..

##### **Geohot** [[00:24:09](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1449)]
I wish I'd read more kernels.

##### **Geohot** [[00:24:09](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1449)]
I wish I'd not read S and P E,

##### **Geohot** [[00:24:11](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1451)]
and I wish I'd read all the state-of-the-art H100 kernels and stuff.

##### **Chenyu** [[00:24:15](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1455)]
So what better way to force us to read the kernels

##### **Geohot** [[00:24:18](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1458)]
than to actually write the kernels,

##### **Geohot** [[00:24:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1459)]
but in our higher-level abstracted language?

##### **Geohot** [[00:24:23](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1463)]
Instead of writing the kernels in..

##### **Geohot** [[00:24:26](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1466)]
Because, finally, if your middleware cannot express the ideas,

##### **Geohot** [[00:24:30](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1470)]
your front-end can never, ever find them.

##### **Chenyu** [[00:24:34](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1474)]
You have to make sure that your middleware can express the ideas, right?

##### **Geohot** [[00:24:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1477)]
And I did a whole bunch of things wrong because of that.

##### **Geohot** [[00:24:39](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1479)]
But everything's fixed now.

##### **Geohot** [[00:24:41](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1481)]
Like, with range of eye and stuff,

##### **Geohot** [[00:24:43](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1483)]
like, that's fully state-of-the-art.

##### **Geohot** [[00:24:47](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1487)]
There is no..

##### **Chenyu** [[00:24:47](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1487)]
There is no..

##### **Geohot** [[00:24:50](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1490)]
You know, I remember a few people brought this up.

##### **Geohot** [[00:24:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1492)]
A few people who worked on AI compilers, like,

##### **Geohot** [[00:24:53](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1493)]
brought this up when they saw ShapeTracker and stuff,

##### **Geohot** [[00:24:55](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1495)]
and they're like, well, how do you do locals?

##### **Geohot** [[00:24:57](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1497)]
Like, well, you know, here, we have these, like, things to do it.

##### **Chenyu** [[00:25:00](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1500)]
And they're like, yeah, yeah, that's not generic.

##### **Geohot** [[00:25:01](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1501)]
But the range of eye one is fully..

##### **Geohot** [[00:25:04](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1504)]
is fully generic and modern.

##### **Geohot** [[00:25:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1506)]
It can do everything Halide and TVM can do.

##### **Geohot** [[00:25:09](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1509)]
And..

##### **Geohot** [[00:25:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1512)]
Yeah, I mean, I'm curious.

##### **Chenyu** [[00:25:13](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1513)]
And the thing that we really need to find out

##### **Geohot** [[00:25:17](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1517)]
is, is there anything that our language can't express?

##### **Geohot** [[00:25:20](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1520)]
Because if there's something our language can't express,

##### **Geohot** [[00:25:22](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1522)]
it's so much better to figure this out now

##### **Geohot** [[00:25:24](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1524)]
than to figure this out in, you know,

##### **Geohot** [[00:25:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1527)]
after diving into search

##### **Chenyu** [[00:25:28](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1528)]
and then having to rewrite the search thing an extra time.

##### **Geohot** [[00:25:32](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1532)]
So that's why we're writing kernels.

##### **Geohot** [[00:25:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1536)]
I'm not asking for 100 kernels here.

##### **Geohot** [[00:25:39](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1539)]
I'm asking for four.

##### **Geohot** [[00:25:42](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1542)]
And they're all, they're all, they're all, you know,

##### **Geohot** [[00:25:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1545)]
cute and different enough in their own way.

##### **Chenyu** [[00:25:47](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1547)]
This is not a lot of repetitive work.

##### **Geohot** [[00:25:49](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1549)]
Nobody's asking for a kernel for conv2d

##### **Geohot** [[00:25:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1554)]
transposed dilated here.

##### **Geohot** [[00:25:56](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1556)]
We're asking for a kernel that, you know, two kernels.

##### **Geohot** [[00:25:59](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1559)]
We're asking for a GEMM and a flash attention,

##### **Geohot** [[00:26:00](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1560)]
which are like the two demos in every, in every fast kernel library.

##### **Chenyu** [[00:26:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1567)]
What happened to conv2d?

##### **Geohot** [[00:26:10](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1570)]
Do we have the best conv2d?

##### **Geohot** [[00:26:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1572)]
Do we plan to?

##### **Geohot** [[00:26:15](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1575)]
What if the researcher wants to use conv?

##### **Geohot** [[00:26:17](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1577)]
Then in three years, the automated search will be good.

##### **Geohot** [[00:26:21](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1581)]
Okay.

##### **Chenyu** [[00:26:22](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1582)]
Or they're welcome to write it in the uop language,

##### **Geohot** [[00:26:24](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1584)]
which should be fully documented and fully interop.

##### **Geohot** [[00:26:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1587)]
I mean, really the uop language right now,

##### **Geohot** [[00:26:29](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1589)]
we have this tensor.custom kernel,

##### **Geohot** [[00:26:31](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1591)]
but we shouldn't have that.

##### **Geohot** [[00:26:32](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1592)]
There should be no reason that you can't.

##### **Chenyu** [[00:26:35](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1595)]
Just construct a uop and throw it to a tensor.

##### **Geohot** [[00:26:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1597)]
Yes.

##### **Geohot** [[00:26:38](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1598)]
You should be able to,

##### **Geohot** [[00:26:39](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1599)]
you should be able to fully construct all of the kernel stuff in the,

##### **Geohot** [[00:26:41](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1601)]
in the big graph and it should just work.

##### **Geohot** [[00:26:43](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1603)]
I think it's all differentiable too.

##### **Chenyu** [[00:26:47](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1607)]
Now your derivative may not be a smart way to do your kernel,

##### **Geohot** [[00:26:53](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1613)]
but that comes down to that.

##### **Geohot** [[00:26:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1614)]
That's like the Sigma trick again.

##### **Geohot** [[00:26:56](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1616)]
So it was going to be stuff like that.

##### **Geohot** [[00:26:59](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1619)]
Right.

##### **Geohot** [[00:26:59](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1619)]
You can express stuff as like,

##### **Chenyu** [[00:27:00](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1620)]
you know,

##### **Geohot** [[00:27:01](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1621)]
yeah,

##### **Geohot** [[00:27:01](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1621)]
there's probably,

##### **Geohot** [[00:27:01](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1621)]
you know,

##### **Geohot** [[00:27:02](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1622)]
we probably have some syntax to like,

##### **Geohot** [[00:27:03](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1623)]
you can write stuff in tensor and be like,

##### **Chenyu** [[00:27:05](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1625)]
no,

##### **Geohot** [[00:27:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1626)]
I want to override this derivative with this other stuff.

##### **Geohot** [[00:27:09](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1629)]
Also written in tensor.

##### **Geohot** [[00:27:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1632)]
I mean,

##### **Geohot** [[00:27:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1632)]
the way that this goes is like,

##### **Geohot** [[00:27:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1634)]
so more and more things migrate out of tensor and ops into,

##### **Chenyu** [[00:27:17](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1637)]
into mixins.

##### **Geohot** [[00:27:20](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1640)]
So tensor will just become this very small wrapper.

##### **Geohot** [[00:27:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1647)]
You know,

##### **Geohot** [[00:27:28](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1648)]
it's just,

##### **Geohot** [[00:27:28](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1648)]
it's really a container class for you off and hold the pointer.

##### **Geohot** [[00:27:30](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1650)]
You often,

##### **Chenyu** [[00:27:30](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1650)]
that's pretty much it.

##### **Geohot** [[00:27:32](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1652)]
yeah.

##### **Geohot** [[00:27:34](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1654)]
And then you have this like language that you can use.

##### **Geohot** [[00:27:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1656)]
I mean,

##### **Geohot** [[00:27:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1657)]
tensors and uops are basically identical.

##### **Geohot** [[00:27:38](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1658)]
The old one is,

##### **Chenyu** [[00:27:39](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1659)]
the only time you use a uop instead of a tensor,

##### **Geohot** [[00:27:40](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1660)]
you can use a uop instead of a tensor.

##### **Geohot** [[00:27:42](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1662)]
If you never actually want to reference this thing later,

##### **Geohot** [[00:27:44](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1664)]
the only thing a tensor is,

##### **Geohot** [[00:27:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1665)]
is it is this a pointer to uop.

##### **Geohot** [[00:27:47](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1667)]
So you can keep this pointer around and it promises you that.

##### **Chenyu** [[00:27:50](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1670)]
Yeah.

##### **Geohot** [[00:27:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1671)]
Like if you realize the buffer that realized buffer doesn't actually change the

##### **Geohot** [[00:27:55](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1675)]
uops because you ups are immutable.

##### **Geohot** [[00:27:57](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1677)]
The tensor is what actually changes.

##### **Geohot** [[00:28:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1688)]
Yeah.

##### **Geohot** [[00:28:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1688)]
I mean,

##### **Chenyu** [[00:28:09](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1689)]
I need everyone here working on this contract that this is,

##### **Geohot** [[00:28:11](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1691)]
I,

##### **Geohot** [[00:28:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1692)]
this is the entire company depends on us.

##### **Geohot** [[00:28:15](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1695)]
Um,

##### **Geohot** [[00:28:16](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1696)]
if we fail at this,

##### **Geohot** [[00:28:17](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1697)]
I think we should shut down because if we get,

##### **Chenyu** [[00:28:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1699)]
I mean,

##### **Geohot** [[00:28:20](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1700)]
if we can't do this,

##### **Geohot** [[00:28:20](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1700)]
we can't do this,

##### **Geohot** [[00:28:21](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1701)]
but I don't see why we can't,

##### **Geohot** [[00:28:23](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1703)]
let's just do this.

##### **Geohot** [[00:28:25](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1705)]
All right.

##### **Chenyu** [[00:28:25](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1705)]
I don't care how much we have to encode.

##### **Geohot** [[00:28:29](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1709)]
We'll clean that up later.

##### **Geohot** [[00:28:31](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1711)]
We'll actually clean it up later or we won't,

##### **Geohot** [[00:28:33](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1713)]
or it'll be like the DSP contract where we don't,

##### **Geohot** [[00:28:34](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1714)]
or we go to something else and that's fine too.

##### **Geohot** [[00:28:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1717)]
Right?

##### **Chenyu** [[00:28:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1717)]
You take whatever learning,

##### **Geohot** [[00:28:38](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1718)]
you,

##### **Geohot** [[00:28:38](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1718)]
you have away from this,

##### **Geohot** [[00:28:40](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1720)]
but there's no better way to actually make progress on a piece of software

##### **Geohot** [[00:28:43](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1723)]
than to try to use it,

##### **Geohot** [[00:28:44](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1724)]
actually do something.

##### **Chenyu** [[00:28:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1731)]
Okay.

##### **Geohot** [[00:29:16](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1756)]
So I think you were discussing SQTT before we joined back.

##### **Geohot** [[00:29:26](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1766)]
I can talk about this.

##### **Geohot** [[00:29:29](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1769)]
So I merged the UI in this right now.

##### **Geohot** [[00:29:35](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1775)]
It's using the raw cam decoder.

##### **Geohot** [[00:29:39](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1779)]
I think like if you run with SQTT equals one and with,

##### **Chenyu** [[00:29:44](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1784)]
you'll see if there are any error messages and it will guide you through how to download

##### **Geohot** [[00:29:49](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1789)]
the decoder.

##### **Geohot** [[00:29:53](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1793)]
It did some work on just writing assembly kernels and then timing,

##### **Geohot** [[00:30:00](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1800)]
comparing raw cams stuff with the AMD tooling,

##### **Geohot** [[00:30:04](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1804)]
the other one,

##### **Geohot** [[00:30:05](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1805)]
the RGP.

##### **Chenyu** [[00:30:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1806)]
And I find a lot of discrepancy.

##### **Geohot** [[00:30:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1808)]
And I have no way to debug it because it's like a cool source thing.

##### **Geohot** [[00:30:13](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1813)]
It's basically a black box.

##### **Geohot** [[00:30:15](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1815)]
So I just find myself keep giving on like not knowing what's going on with the decoder,

##### **Geohot** [[00:30:25](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1825)]
but sometimes it's just wrong.

##### **Geohot** [[00:30:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1827)]
Does the RGP tool link to that decoder and use it?

##### **Chenyu** [[00:30:35](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1835)]
No,

##### **Geohot** [[00:30:35](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1835)]
I think it uses a difference.

##### **Geohot** [[00:30:38](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1838)]
Oh,

##### **Geohot** [[00:30:39](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1839)]
okay.

##### **Geohot** [[00:30:39](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1839)]
Then this is,

##### **Geohot** [[00:30:40](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1840)]
this is unmaintained crap and we have to write around.

##### **Chenyu** [[00:30:44](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1844)]
That's what I'm planning to do.

##### **Geohot** [[00:30:46](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1846)]
I think I was going to bring it up in.

##### **Geohot** [[00:30:49](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1849)]
No,

##### **Geohot** [[00:30:49](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1849)]
actually like the Linux tool,

##### **Geohot** [[00:30:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1851)]
and which is like RGP,

##### **Geohot** [[00:30:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1852)]
it's like for gaming and this stuff.

##### **Chenyu** [[00:30:55](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1855)]
And for AI is this tool that we use.

##### **Geohot** [[00:30:59](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1859)]
And I think the first thing is what we really need to do is just to compare the rock prof.

##### **Geohot** [[00:31:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1867)]
Um,

##### **Geohot** [[00:31:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1868)]
like they own Linux profiler and yeah,

##### **Geohot** [[00:31:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1872)]
see what results it shows.

##### **Geohot** [[00:31:16](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1876)]
Yeah,

##### **Chenyu** [[00:31:16](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1876)]
that seems reasonable.

##### **Geohot** [[00:31:17](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1877)]
I ran.

##### **Geohot** [[00:31:20](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1880)]
Yeah,

##### **Geohot** [[00:31:21](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1881)]
I ran tiny R seven.

##### **Geohot** [[00:31:25](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1885)]
I ran this on tiny R seven.

##### **Geohot** [[00:31:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1887)]
It doesn't still show the stuff that I wanted to show like on my test on simple Mac movie.

##### **Chenyu** [[00:31:33](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1893)]
I showed some things,

##### **Geohot** [[00:31:34](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1894)]
but like on some other tests,

##### **Geohot** [[00:31:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1896)]
it's just empty.

##### **Geohot** [[00:31:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1897)]
Okay.

##### **Geohot** [[00:31:38](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1898)]
But the whole problem with all these external dependencies that they have no way to debug it.

##### **Geohot** [[00:31:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1905)]
Once something is wrong.

##### **Chenyu** [[00:31:46](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1906)]
Yeah.

##### **Geohot** [[00:31:48](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1908)]
You need to limit Shader engines.

##### **Geohot** [[00:31:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1911)]
So our runtime does that automatically,

##### **Geohot** [[00:31:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1914)]
but I think you should provide some variables to HSA.

##### **Geohot** [[00:32:00](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1920)]
Because actually they capture only like the first Shader engine.

##### **Geohot** [[00:32:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1928)]
So yeah,

##### **Chenyu** [[00:32:09](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1929)]
you need to limit this somehow.

##### **Geohot** [[00:32:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1932)]
And that's definitely possible.

##### **Geohot** [[00:32:13](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1933)]
I've seen somewhere in their dogs.

##### **Geohot** [[00:32:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1934)]
I can look into this.

##### **Geohot** [[00:32:24](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1944)]
And actually,

##### **Geohot** [[00:32:25](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1945)]
maybe we also can validate.

##### **Chenyu** [[00:32:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1947)]
I think,

##### **Geohot** [[00:32:28](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1948)]
uh,

##### **Geohot** [[00:32:30](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1950)]
am I 350?

##### **Geohot** [[00:32:32](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1952)]
Maybe,

##### **Geohot** [[00:32:34](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1954)]
maybe it's their primary target.

##### **Geohot** [[00:32:35](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1955)]
So we can just see if it works.

##### **Chenyu** [[00:32:38](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1958)]
Fine on my 350 and make this work for the contract.

##### **Geohot** [[00:32:44](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1964)]
My guess would be the best recorded GPU is at my 300.

##### **Geohot** [[00:32:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1971)]
It seems like there's stuff for my 350 isn't quite there yet.

##### **Geohot** [[00:33:01](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1981)]
But yeah,

##### **Geohot** [[00:33:02](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1982)]
and we can try it.

##### **Geohot** [[00:33:03](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1983)]
We can try it on either.

##### **Chenyu** [[00:33:05](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1985)]
Yeah.

##### **Geohot** [[00:33:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1986)]
I mean,

##### **Geohot** [[00:33:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1986)]
I like the idea of just just comparing it.

##### **Geohot** [[00:33:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1988)]
To the AMD tooling,

##### **Geohot** [[00:33:11](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1991)]
seeing seeing what they're using.

##### **Geohot** [[00:33:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1994)]
I mean,

##### **Chenyu** [[00:33:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=1994)]
I'm also I'm also interested in just starting to parse SQTT ourselves.

##### **Geohot** [[00:33:20](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2000)]
It's very interesting.

##### **Geohot** [[00:33:21](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2001)]
What like we're going to have to eventually because like what's the GPU actually measuring?

##### **Geohot** [[00:33:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2007)]
That's the interesting thing.

##### **Geohot** [[00:33:28](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2008)]
I don't want a lot of the abstractions on GPUs are really bad.

##### **Geohot** [[00:33:33](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2013)]
Like there's whole idea of,

##### **Chenyu** [[00:33:35](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2015)]
of,

##### **Geohot** [[00:33:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2016)]
you know,

##### **Geohot** [[00:33:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2017)]
when you put,

##### **Geohot** [[00:33:38](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2018)]
when you type float a and CUDA that that's actually a float VEC 32.

##### **Geohot** [[00:33:43](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2023)]
It's just this is a wrong abstraction.

##### **Geohot** [[00:33:44](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2024)]
It might have made sense for gaming shaders,

##### **Chenyu** [[00:33:46](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2026)]
but doesn't make sense for AI.

##### **Geohot** [[00:33:50](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2030)]
So yeah,

##### **Geohot** [[00:33:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2031)]
you know,

##### **Geohot** [[00:33:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2031)]
I like the idea of just cutting through all these GPU abstractions.

##### **Geohot** [[00:33:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2034)]
We started our own but you know,

##### **Geohot** [[00:33:56](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2036)]
don't get too lost in a rabbit hole stick to things that are sick to things that are grounded.

##### **Chenyu** [[00:34:02](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2042)]
And if we don't replicate RGB perfectly,

##### **Geohot** [[00:34:04](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2044)]
I want to know why.

##### **Geohot** [[00:34:10](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2050)]
I'll try to see if like we are doing something wrong.

##### **Geohot** [[00:34:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2054)]
Maybe it's an our problem.

##### **Geohot** [[00:34:17](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2057)]
Yeah,

##### **Geohot** [[00:34:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2059)]
even like the simplest stuff that they write mismatch.

##### **Chenyu** [[00:34:23](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2063)]
That's kind of like I want to understand what the actual blob that SQTT is outputting is.

##### **Geohot** [[00:34:30](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2070)]
On my USB GPU.

##### **Geohot** [[00:34:32](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2072)]
I have so many books.

##### **Geohot** [[00:34:35](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2075)]
GFX 11 is much nicer.

##### **Geohot** [[00:34:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2076)]
Again,

##### **Geohot** [[00:34:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2077)]
a situation to the TinyBox and most of the stuff that works the USB GPU crashes every single time.

##### **Chenyu** [[00:34:44](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2084)]
That's why I have.

##### **Geohot** [[00:34:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2085)]
Why is that because of GFX 12 or because of the USB?

##### **Geohot** [[00:34:56](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2096)]
You can try SP has any thing to do with it.

##### **Geohot** [[00:35:00](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2100)]
Well,

##### **Geohot** [[00:35:01](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2101)]
if you think it's GFX 12,

##### **Geohot** [[00:35:02](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2102)]
try it on tiny H3 and see if there is the problem.

##### **Chenyu** [[00:35:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2106)]
I think.

##### **Geohot** [[00:35:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2107)]
Very well could be the USB.

##### **Geohot** [[00:35:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2108)]
You're on USB 4,

##### **Geohot** [[00:35:09](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2109)]
right?

##### **Geohot** [[00:35:11](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2111)]
Yeah,

##### **Geohot** [[00:35:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2112)]
right.

##### **Chenyu** [[00:35:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2112)]
That should have less bugs,

##### **Geohot** [[00:35:13](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2113)]
but yeah,

##### **Geohot** [[00:35:15](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2115)]
I mean,

##### **Geohot** [[00:35:16](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2116)]
what do you see?

##### **Geohot** [[00:35:17](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2117)]
I mean,

##### **Geohot** [[00:35:17](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2117)]
like,

##### **Chenyu** [[00:35:20](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2120)]
oh,

##### **Geohot** [[00:35:20](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2120)]
it's precious.

##### **Geohot** [[00:35:21](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2121)]
Like it gives very random counter values like very huge.

##### **Geohot** [[00:35:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2127)]
So you 32 bit numbers that absolutely make no sense or sometimes negative counter values because something overflowed.

##### **Geohot** [[00:35:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2137)]
Yeah,

##### **Geohot** [[00:35:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2137)]
you can't see what you're doing.

##### **Chenyu** [[00:35:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2137)]
but you can see if you can reproduce it on H3.

##### **Geohot** [[00:35:40](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2140)]
Which has a which has a GFX 12,

##### **Geohot** [[00:35:42](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2142)]
you have a GFX 12 on the USB GPM.

##### **Geohot** [[00:35:43](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2143)]
So.

##### **Geohot** [[00:35:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2145)]
Yeah.

##### **Geohot** [[00:35:48](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2148)]
So I think our plan is to first start with rock and stuff and then.

##### **Chenyu** [[00:35:55](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2155)]
Do you think it's the USB or do you think it's the 12?

##### **Geohot** [[00:36:03](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2163)]
I think I know I've tested my GFX 11 on the USB.

##### **Geohot** [[00:36:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2167)]
It was fine.

##### **Geohot** [[00:36:10](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2170)]
I didn't know.

##### **Geohot** [[00:36:11](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2171)]
Right.

##### **Geohot** [[00:36:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2174)]
Yeah.

##### **Chenyu** [[00:36:18](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2178)]
Yeah.

##### **Geohot** [[00:36:20](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2180)]
I don't know.

##### **Geohot** [[00:36:20](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2180)]
But yeah,

##### **Geohot** [[00:36:20](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2180)]
if you,

##### **Geohot** [[00:36:21](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2181)]
I mean,

##### **Geohot** [[00:36:21](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2181)]
if you're seeing problems,

##### **Chenyu** [[00:36:22](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2182)]
just like figure out the simplest way to reproduce them and post them and we'll improve whatever it is.

##### **Geohot** [[00:36:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2196)]
Hey,

##### **Geohot** [[00:36:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2197)]
how good is our tiny kitten?

##### **Geohot** [[00:36:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2205)]
It works.

##### **Geohot** [[00:36:46](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2206)]
It's not very fast yet.

##### **Geohot** [[00:36:49](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2209)]
Working on correctness first.

##### **Chenyu** [[00:36:53](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2213)]
But does it differ from how under kittens is doing it?

##### **Geohot** [[00:36:57](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2217)]
Like are the registers in the same place and locals in the same place?

##### **Geohot** [[00:37:01](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2221)]
Yeah.

##### **Geohot** [[00:37:02](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2222)]
So all the indexing matches Thunder kittens exactly.

##### **Geohot** [[00:37:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2226)]
And then,

##### **Geohot** [[00:37:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2227)]
the only thing is,

##### **Chenyu** [[00:37:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2227)]
is I've disabled all the optimization so I can actually read all the kernels.

##### **Geohot** [[00:37:10](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2230)]
So like nothing's upcasted,

##### **Geohot** [[00:37:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2232)]
nothing's enrolled.

##### **Geohot** [[00:37:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2234)]
That really kind of shouldn't matter,

##### **Geohot** [[00:37:18](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2238)]
especially with cool.

##### **Geohot** [[00:37:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2239)]
There are some stuff that I haven't implemented yet,

##### **Chenyu** [[00:37:21](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2241)]
just so it's easier for me to think about the kernel.

##### **Geohot** [[00:37:25](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2245)]
So local swizzling isn't done.

##### **Geohot** [[00:37:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2247)]
So there's S man bank conflicts.

##### **Geohot** [[00:37:30](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2250)]
Oh yeah.

##### **Geohot** [[00:37:31](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2251)]
I mean,

##### **Geohot** [[00:37:32](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2252)]
now I'm going to kill you.

##### **Chenyu** [[00:37:33](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2253)]
It's not,

##### **Geohot** [[00:37:33](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2253)]
it's not the same index.

##### **Geohot** [[00:37:35](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2255)]
Uh,

##### **Geohot** [[00:37:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2256)]
yes,

##### **Geohot** [[00:37:38](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2258)]
but they do that very,

##### **Geohot** [[00:37:40](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2260)]
it just have a function on the like S man tile called like dot IDX.

##### **Chenyu** [[00:37:47](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2267)]
And then you pass a standard index and it gives you the swizzled index back.

##### **Geohot** [[00:37:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2272)]
Yeah.

##### **Geohot** [[00:37:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2272)]
So I just didn't.

##### **Geohot** [[00:37:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2274)]
Yeah.

##### **Geohot** [[00:37:55](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2275)]
So I just didn't do that yet.

##### **Geohot** [[00:37:56](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2276)]
So I can think about where stuff is placed.

##### **Chenyu** [[00:38:00](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2280)]
Yeah.

##### **Geohot** [[00:38:01](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2281)]
I mean,

##### **Geohot** [[00:38:01](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2281)]
that's the,

##### **Geohot** [[00:38:02](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2282)]
so the key thing to do for,

##### **Geohot** [[00:38:04](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2284)]
for,

##### **Geohot** [[00:38:04](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2284)]
for tiny kittens is to get fast GEMMs everywhere.

##### **Chenyu** [[00:38:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2288)]
Yeah.

##### **Geohot** [[00:38:13](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2293)]
Like yeah.

##### **Geohot** [[00:38:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2294)]
And just make sure that every bite is being accessed in the same order in both tiny kittens and thunder kittens.

##### **Geohot** [[00:38:22](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2302)]
Mm.

##### **Geohot** [[00:38:23](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2303)]
Yeah.

##### **Geohot** [[00:38:24](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2304)]
Don't worry about upcast.

##### **Chenyu** [[00:38:25](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2305)]
Don't worry about unroll.

##### **Geohot** [[00:38:26](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2306)]
Those things don't matter.

##### **Geohot** [[00:38:28](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2308)]
Yeah.

##### **Geohot** [[00:38:29](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2309)]
Also really,

##### **Geohot** [[00:38:30](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2310)]
that's the kernel source.

##### **Geohot** [[00:38:33](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2313)]
Yeah.

##### **Chenyu** [[00:38:34](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2314)]
It makes it hard to,

##### **Geohot** [[00:38:34](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2314)]
it's hard to read.

##### **Geohot** [[00:38:35](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2315)]
I mean,

##### **Geohot** [[00:38:35](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2315)]
so upcast itself doesn't matter,

##### **Geohot** [[00:38:38](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2318)]
but doing the split does matter,

##### **Geohot** [[00:38:40](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2320)]
but you can use dot loop.

##### **Chenyu** [[00:38:44](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2324)]
If you look at the AMD,

##### **Geohot** [[00:38:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2325)]
you up matmo,

##### **Geohot** [[00:38:47](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2327)]
there's just a bunch of like tiny loops and those tiny loops will be automatically unrolled by clang.

##### **Geohot** [[00:38:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2332)]
And it's,

##### **Geohot** [[00:38:53](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2333)]
it's the second.

##### **Geohot** [[00:38:56](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2336)]
Okay.

##### **Chenyu** [[00:39:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2346)]
Show me the other prop.

##### **Geohot** [[00:39:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2346)]
I use only one of them.

##### **Geohot** [[00:39:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2348)]
commerical beholder Grey0 and usu,

##### **Geohot** [[00:39:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2352)]
but when I see a link to thisEMERIC CL app,

##### **Geohot** [[00:39:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2352)]
C bleibt comunic niet größer als zwarte groen.

##### **Geohot** [[00:39:13](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2353)]
So it's,

##### **Chenyu** [[00:39:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2354)]
he is shaking and shaking,

##### **Geohot** [[00:39:15](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2355)]
Generally speaking.

##### **Geohot** [[00:39:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2359)]
C is also a user code isrterlich.

##### **Geohot** [[00:39:23](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2363)]
but it's a great user,

##### **Geohot** [[00:39:23](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2363)]
but it doesn't have a blast feature to have to use the shifter.

##### **Geohot** [[00:39:25](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2365)]
So it's not easy,

##### **Chenyu** [[00:39:28](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2368)]
sleep.

##### **Geohot** [[00:39:29](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2369)]
em.,

##### **Geohot** [[00:39:32](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2372)]
Ench don't know what it is.

##### **Geohot** [[00:39:34](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2374)]
years ago, that was the wrong thing to focus on.

##### **Geohot** [[00:39:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2376)]
Because if we tried to do that, we would have ended up

##### **Geohot** [[00:39:38](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2378)]
with a ton of hard-coded crap. But now,

##### **Chenyu** [[00:39:40](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2380)]
I think we're to the point where we need to

##### **Geohot** [[00:39:42](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2382)]
focus on making GEMM as

##### **Geohot** [[00:39:44](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2384)]
fast as Kublos on

##### **Geohot** [[00:39:46](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2386)]
all of these GPUs. As fast as Kublos,

##### **Geohot** [[00:39:48](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2388)]
as fast as Rockblos.

##### **Geohot** [[00:39:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2391)]
Yeah, we gotta be,

##### **Chenyu** [[00:39:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2392)]
we gotta have the fastest GEMMs, basically.

##### **Geohot** [[00:39:55](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2395)]
And if we can't have

##### **Geohot** [[00:39:56](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2396)]
the fastest GEMMs for some reason, we gotta figure out

##### **Geohot** [[00:39:58](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2398)]
what we need to add, because we know it's possible.

##### **Geohot** [[00:40:02](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2402)]
Yep.

##### **Geohot** [[00:40:05](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2405)]
Yeah.

##### **Chenyu** [[00:40:05](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2405)]
But no, I mean, I think that this,

##### **Geohot** [[00:40:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2407)]
the way that the UOB

##### **Geohot** [[00:40:09](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2409)]
abstraction works, it's hard to

##### **Geohot** [[00:40:11](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2411)]
write anything really bad in it.

##### **Geohot** [[00:40:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2414)]
Like,

##### **Geohot** [[00:40:15](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2415)]
in CUDA kernels, you can write things that are just

##### **Chenyu** [[00:40:17](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2417)]
really bad, and that nothing could ever

##### **Geohot** [[00:40:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2419)]
reason about. But

##### **Geohot** [[00:40:20](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2420)]
I think in UOBs, it's kind of hard.

##### **Geohot** [[00:40:25](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2425)]
Yeah.

##### **Geohot** [[00:40:29](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2429)]
Yeah, and I mean, and then we can

##### **Geohot** [[00:40:31](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2431)]
like, I think for a lot

##### **Chenyu** [[00:40:32](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2432)]
of things, I think like, I was thinking

##### **Geohot** [[00:40:34](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2434)]
about

##### **Geohot** [[00:40:34](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2434)]
like, yeah, the max unrolling and flash attention,

##### **Geohot** [[00:40:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2436)]
right? Like, the way to really write this

##### **Geohot** [[00:40:38](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2438)]
search is not to,

##### **Geohot** [[00:40:40](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2440)]
like, with the A-range,

##### **Chenyu** [[00:40:42](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2442)]
I think it's similar to the A-range folding.

##### **Geohot** [[00:40:44](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2444)]
With A-range folding, it was easy to know what the kernel

##### **Geohot** [[00:40:46](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2446)]
should be, but in this one, it's kind of harder

##### **Geohot** [[00:40:48](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2448)]
to know what the kernel should be, but it'll be nice to have the two

##### **Geohot** [[00:40:50](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2450)]
side-by-side in Viz. Oh, here's the one with the max.

##### **Geohot** [[00:40:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2452)]
Here's the one without the max. Okay, cool. Now I see

##### **Chenyu** [[00:40:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2454)]
the transformation, and we can think

##### **Geohot** [[00:40:56](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2456)]
about if that transformation can be broken into pieces,

##### **Geohot** [[00:40:58](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2458)]
how we might want to search and find

##### **Geohot** [[00:41:00](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2460)]
that. And I think

##### **Geohot** [[00:41:02](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2462)]
there's this intermediate stage as well,

##### **Geohot** [[00:41:04](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2464)]
where, you know, we're not going to be able to do that.

##### **Chenyu** [[00:41:04](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2464)]
We're not going to be able to do that.

##### **Geohot** [[00:41:05](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2465)]
where, like, the

##### **Geohot** [[00:41:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2466)]
beauty of the hand-coded kernels is

##### **Geohot** [[00:41:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2468)]
all the optimizations still work on them.

##### **Geohot** [[00:41:11](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2471)]
So we could get

##### **Geohot** [[00:41:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2472)]
to a point where you can write the hand-coded kernels

##### **Chenyu** [[00:41:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2474)]
in a dumb style. Like, it's

##### **Geohot** [[00:41:16](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2476)]
the full intermediate, where

##### **Geohot** [[00:41:18](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2478)]
you can write them in a dumb style and apply the

##### **Geohot** [[00:41:20](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2480)]
optimizations to them. Like,

##### **Geohot** [[00:41:22](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2482)]
one of the things about

##### **Geohot** [[00:41:24](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2484)]
TinyGrad that is nowhere else

##### **Chenyu** [[00:41:26](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2486)]
is that we have this

##### **Geohot** [[00:41:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2487)]
unified op space.

##### **Geohot** [[00:41:30](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2490)]
It's not perfectly unified.

##### **Geohot** [[00:41:32](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2492)]
There are sometimes different ops that you can use

##### **Geohot** [[00:41:34](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2494)]
at different times, but this is becoming less and less. You can now use movement ops. You can use

##### **Geohot** [[00:41:40](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2500)]
movement ops in the UOP kernels and then applying an index to a movement op can actually be done

##### **Chenyu** [[00:41:47](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2507)]
as late as you want. So the goal is to eventually unify this entire space so every op can be used

##### **Geohot** [[00:41:55](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2515)]
everywhere. Some ops can just be removed. And that's the magic.

##### **Geohot** [[00:42:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2528)]
Oh, on that, one of these projects that we have to do, someone's got to do this soon, is

##### **Geohot** [[00:42:16](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2536)]
removing images from the high level. Images should not be a tensor dtype. Images should be a load and

##### **Geohot** [[00:42:22](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2542)]
store optimization in the kernels.

##### **Geohot** [[00:42:26](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2546)]
Oh, yeah. It's not that we have to focus every single thing on the contract. We just have to focus 70% on the contract.

##### **Chenyu** [[00:42:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2557)]
How do you apply Comp2D?

##### **Geohot** [[00:42:42](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2562)]
It's like WinOber, right? At a very high level, you use a different algorithm because you know later it will be optimized.

##### **Geohot** [[00:42:48](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2568)]
Oh, for images? Yeah. So, okay. The images are two things. So it's actually not a different algorithm.

##### **Geohot** [[00:42:53](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2573)]
The algorithm for images is a very simple algorithm. It's just a very simple algorithm. It's a very simple algorithm.

##### **Geohot** [[00:42:55](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2575)]
The image is identical, but the memory placement is different.

##### **Geohot** [[00:42:57](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2577)]
It's simple. It's a permute.

##### **Chenyu** [[00:42:58](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2578)]
It's just a permute on the things.

##### **Geohot** [[00:43:00](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2580)]
But I'm even saying to keep that, and just basically use, like, image equals one..

##### **Geohot** [[00:43:05](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2585)]
No, that's what I mean, Joe me to keep that up.

##### **Geohot** [[00:43:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2586)]
Yeah, you can even keep that up. But that algorithm, it's not Funigrad. towers, not that complex.

##### **Geohot** [[00:43:11](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2591)]
Winograd is also not that complex. It's��

##### **Geohot** [[00:43:13](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2593)]
Well, minusums to address low class was past into amoebas, so let's put it back in a new cleaner model.

##### **Chenyu** [[00:43:15](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2595)]
Winograd is changing the math, the image WF doesn't change the math it's the same. It just, it just, uh, It's changing the order class.

##### **Geohot** [[00:43:25](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2605)]
in memory. It's not

##### **Geohot** [[00:43:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2607)]
NCHW. It's not

##### **Geohot** [[00:43:29](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2609)]
NHWC. It's

##### **Geohot** [[00:43:31](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2611)]
NC divided by 4

##### **Geohot** [[00:43:33](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2613)]
HWC mod 4.

##### **Chenyu** [[00:43:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2616)]
Something.

##### **Geohot** [[00:43:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2616)]
Something. And this turns out,

##### **Geohot** [[00:43:39](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2619)]
these turn out to be a lot of the fast formats

##### **Geohot** [[00:43:41](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2621)]
on hardware. The DSP.

##### **Geohot** [[00:43:42](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2622)]
That was another big

##### **Geohot** [[00:43:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2625)]
win from the DSP contract.

##### **Chenyu** [[00:43:47](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2627)]
Like, it made me realize

##### **Geohot** [[00:43:49](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2629)]
that that is the key optimization.

##### **Geohot** [[00:43:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2631)]
And we can do it now. With Buffer

##### **Geohot** [[00:43:53](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2633)]
Eyes and Index, you can

##### **Geohot** [[00:43:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2634)]
arbitrarily split and permute

##### **Geohot** [[00:43:58](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2638)]
across the Buffer

##### **Chenyu** [[00:43:59](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2639)]
Eyes and Index.

##### **Geohot** [[00:44:02](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2642)]
And

##### **Geohot** [[00:44:03](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2643)]
you can do this in such a way, it's really

##### **Geohot** [[00:44:05](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2645)]
nice, because you can do this using

##### **Geohot** [[00:44:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2647)]
movement ops on the Buffer Eyes. So you're like,

##### **Geohot** [[00:44:09](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2649)]
what if the Buffer Eyes has two index children?

##### **Chenyu** [[00:44:10](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2650)]
Well, if I want to permute it,

##### **Geohot** [[00:44:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2652)]
all I need to do is switch

##### **Geohot** [[00:44:15](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2655)]
them in the Buffer Eyes, and let's take a permute op

##### **Geohot** [[00:44:16](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2656)]
on the Buffer Eyes. And then run PM

##### **Geohot** [[00:44:18](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2658)]
mops, and it

##### **Geohot** [[00:44:22](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2662)]
munches the index

##### **Chenyu** [[00:44:22](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2662)]
up to the Buffer Eyes again.

##### **Geohot** [[00:44:25](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2665)]
So yeah, like, it's

##### **Geohot** [[00:44:26](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2666)]
really cool that that's an optimization that you can just

##### **Geohot** [[00:44:28](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2668)]
apply to the Buffer Eyes to

##### **Geohot** [[00:44:30](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2670)]
completely change memory layouts.

##### **Geohot** [[00:44:32](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2672)]
And memory layouts, I mean, memory layouts, this

##### **Chenyu** [[00:44:34](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2674)]
local swizzling thing, is memory

##### **Geohot** [[00:44:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2676)]
layouts also.

##### **Geohot** [[00:44:38](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2678)]
Also, one of the things that Flamit

##### **Geohot** [[00:44:40](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2680)]
used to bring up was the

##### **Geohot** [[00:44:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2685)]
common pattern, often,

##### **Geohot** [[00:44:46](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2686)]
for

##### **Chenyu** [[00:44:48](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2688)]
locals, is to XR.

##### **Geohot** [[00:44:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2691)]
And now we can do

##### **Geohot** [[00:44:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2692)]
that.

##### **Geohot** [[00:44:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2694)]
There's nothing about index that doesn't support XR.

##### **Geohot** [[00:44:58](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2698)]
How do you do that?

##### **Geohot** [[00:45:00](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2700)]
Put in XR.

##### **Chenyu** [[00:45:04](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2704)]
I'll start off.

##### **Geohot** [[00:45:05](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2705)]
Put XR on the index.

##### **Geohot** [[00:45:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2707)]
Oh, just as a new op?

##### **Geohot** [[00:45:09](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2709)]
No, we don't have XR.

##### **Geohot** [[00:45:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2714)]
I don't need a new op.

##### **Geohot** [[00:45:16](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2716)]
Oh, okay.

##### **Chenyu** [[00:45:16](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2716)]
Okay.

##### **Geohot** [[00:45:16](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2716)]
Just use index and with an XR.

##### **Geohot** [[00:45:18](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2718)]
I mean, you can't do it with a movement op, but everything else works.

##### **Geohot** [[00:45:22](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2722)]
You don't need a new op.

##### **Geohot** [[00:45:23](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2723)]
It's just a transformation on the index.

##### **Geohot** [[00:45:32](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2732)]
Chris M., I see you in here.

##### **Chenyu** [[00:45:33](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2733)]
How's the new

##### **Geohot** [[00:45:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2736)]
autogen coming?

##### **Geohot** [[00:45:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2737)]
It's good.

##### **Geohot** [[00:45:39](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2739)]
It's pretty much ready for review.

##### **Geohot** [[00:45:41](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2741)]
There's one thing,

##### **Geohot** [[00:45:43](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2743)]
the NVJIT link thing is kind of broken.

##### **Chenyu** [[00:45:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2745)]
I wrote this up in the PR

##### **Geohot** [[00:45:47](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2747)]
about specifically why that's going on, but basically

##### **Geohot** [[00:45:48](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2748)]
the old ClangDefy was translating

##### **Geohot** [[00:45:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2752)]
the

##### **Geohot** [[00:45:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2752)]
the

##### **Geohot** [[00:45:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2752)]
file incorrectly, but then it just so happened to be exported.

##### **Chenyu** [[00:45:55](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2755)]
So we've got to figure out what to do about that.

##### **Geohot** [[00:45:57](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2757)]
That seems like we honestly might need just a hard code,

##### **Geohot** [[00:45:59](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2759)]
a case, which is a little annoying.

##### **Geohot** [[00:46:01](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2761)]
But Objective-C works.

##### **Geohot** [[00:46:04](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2764)]
It was a little more complicated than I thought it was going to be

##### **Geohot** [[00:46:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2766)]
because of inheritance stuff in Objective-C, but it works now.

##### **Chenyu** [[00:46:10](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2770)]
So that's like I have to fix some MyPy stuff,

##### **Geohot** [[00:46:13](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2773)]
but other than that, it'll be ready for review like this week.

##### **Geohot** [[00:46:17](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2777)]
Awesome.

##### **Geohot** [[00:46:17](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2777)]
Yeah, I'm super excited about this.

##### **Geohot** [[00:46:20](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2780)]
I was running, I was playing with

##### **Geohot** [[00:46:22](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2782)]
with MuttMutt and Coverage last night,

##### **Chenyu** [[00:46:24](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2784)]
and so much of this is dominated by all the crap autogen stuff.

##### **Geohot** [[00:46:28](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2788)]
So, you know, I'm hoping this new one looks nicer.

##### **Geohot** [[00:46:30](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2790)]
Yeah, I'm very excited about this.

##### **Geohot** [[00:46:34](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2794)]
Yeah, should be good.

##### **Geohot** [[00:46:35](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2795)]
Yeah.

##### **Geohot** [[00:46:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2796)]
I mean, even if it doesn't like look nicer on the drop,

##### **Chenyu** [[00:46:38](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2798)]
it's kind of like now we can at least control it.

##### **Geohot** [[00:46:40](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2800)]
That ClangDefy tool is so, every time I've tried to edit it,

##### **Geohot** [[00:46:43](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2803)]
I'm just like, someone's got to rewrite this.

##### **Geohot** [[00:46:44](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2804)]
So I'm really happy to get that.

##### **Geohot** [[00:46:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2812)]
Chenyu, do you want to say something about AMD FP8?

##### **Geohot** [[00:47:01](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2821)]
Hi.

##### **Chenyu** [[00:47:02](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2822)]
Hi.

##### **Geohot** [[00:47:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2827)]
Now I only quantize Q and K in the even index or in layers.

##### **Geohot** [[00:47:18](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2838)]
The loss can go down now.

##### **Geohot** [[00:47:22](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2842)]
So I'm going to try to get the best of both worlds.

##### **Geohot** [[00:47:24](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2844)]
And next I need to try the other combination

##### **Geohot** [[00:47:28](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2848)]
and try the faster FP8 tensor core.

##### **Chenyu** [[00:47:34](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2854)]
The 6060 and 128 tensor core.

##### **Geohot** [[00:47:42](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2862)]
I already get it works better.

##### **Geohot** [[00:47:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2865)]
The beam can't search the fastest kernel every time.

##### **Geohot** [[00:47:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2874)]
The beam does find the fastest kernel with the 606032.

##### **Geohot** [[00:48:01](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2881)]
Yeah.

##### **Geohot** [[00:48:02](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2882)]
Cool.

##### **Chenyu** [[00:48:04](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2884)]
And since beam can only use the only one tensor core shape

##### **Geohot** [[00:48:17](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2897)]
or the specified input outer D type every time.

##### **Geohot** [[00:48:22](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2902)]
Is that the expected behavior?

##### **Geohot** [[00:48:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2907)]
I mean, yeah.

##### **Geohot** [[00:48:28](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2908)]
You can add more stuff to the beam search thing.

##### **Geohot** [[00:48:31](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2911)]
But I think the real thing to do is that we just kind of like

##### **Chenyu** [[00:48:35](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2915)]
that API boundary isn't great.

##### **Geohot** [[00:48:40](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2920)]
Right now, the fact that we have this other language called

##### **Geohot** [[00:48:43](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2923)]
opt-ops to apply optimizations, what you really want to do

##### **Geohot** [[00:48:46](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2926)]
is graph rewrites and add something like a choice UOP.

##### **Geohot** [[00:48:49](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2929)]
Where if there's like three different ways to do the matmall,

##### **Geohot** [[00:48:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2931)]
cool.

##### **Chenyu** [[00:48:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2932)]
It puts in choice.

##### **Geohot** [[00:48:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2932)]
It puts in the three matmalls.

##### **Geohot** [[00:48:53](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2933)]
And that's it.

##### **Geohot** [[00:48:59](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2939)]
OK.

##### **Geohot** [[00:49:00](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2940)]
And another thing I'm going to do is make the train works

##### **Geohot** [[00:49:04](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2944)]
across multi-GPU.

##### **Chenyu** [[00:49:11](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2951)]
Oh, why would that be different for the D type?

##### **Geohot** [[00:49:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2954)]
Anything special there or just need to making sure it's correct?

##### **Geohot** [[00:49:22](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2962)]
You mean the tensor core?

##### **Geohot** [[00:49:25](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2965)]
I mean, you said the next thing you are going to do is multi-GPU

##### **Geohot** [[00:49:29](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2969)]
is because you need to validate that's correct,

##### **Geohot** [[00:49:32](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2972)]
or you already see something that's different for multi-GPU.

##### **Chenyu** [[00:49:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2977)]
Because I expect it to be kind of free since now also multi-GPU

##### **Geohot** [[00:49:43](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2983)]
works and you are just changing some D types.

##### **Geohot** [[00:49:47](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2987)]
Multi-GPU cost the MMF.

##### **Geohot** [[00:49:53](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2993)]
Oh, OK.

##### **Geohot** [[00:49:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2994)]
Oh.

##### **Geohot** [[00:49:55](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2995)]
Is that related to the tensor cores,

##### **Chenyu** [[00:49:58](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=2998)]
or is that something else?

##### **Geohot** [[00:50:02](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3002)]
It then caused by the FP8.

##### **Geohot** [[00:50:05](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3005)]
It can reproduce using the half train with master code.

##### **Geohot** [[00:50:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3014)]
If you can find the smallest repro of that,

##### **Geohot** [[00:50:16](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3016)]
that would be great.

##### **Geohot** [[00:50:17](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3017)]
And then we can look into it.

##### **Chenyu** [[00:50:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3019)]
Yeah.

##### **Geohot** [[00:50:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3019)]
So try.

##### **Geohot** [[00:50:21](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3021)]
Try doing some old reduced examples on multi-GPU,

##### **Geohot** [[00:50:25](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3025)]
then trying to do a memo by sharding one of it on multi-GPU.

##### **Geohot** [[00:50:31](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3031)]
This too should give you the idea for what we're training.

##### **Geohot** [[00:50:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3036)]
OK.

##### **Chenyu** [[00:50:39](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3039)]
Cool.

##### **Geohot** [[00:50:42](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3042)]
I'll say another thing too about custom kernels.

##### **Geohot** [[00:50:44](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3044)]
Like I said, I don't see this ever going away.

##### **Geohot** [[00:50:46](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3046)]
This is not like, this is I think even less specific than the DSP

##### **Geohot** [[00:50:50](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3050)]
thing.

##### **Geohot** [[00:50:50](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3050)]
We always want to support people writing custom kernels.

##### **Chenyu** [[00:50:55](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3055)]
I don't have issue with custom kernels.

##### **Geohot** [[00:50:57](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3057)]
Yeah.

##### **Geohot** [[00:50:57](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3057)]
I mean, it's not, yeah, this isn't like some, right,

##### **Geohot** [[00:51:00](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3060)]
this isn't, this doesn't violate the tiny grad, like,

##### **Geohot** [[00:51:05](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3065)]
one of the goals is to never have abstractions that leak.

##### **Geohot** [[00:51:09](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3069)]
You never want your abstractions to leak at all.

##### **Chenyu** [[00:51:11](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3071)]
Oh, we just have this one thing.

##### **Geohot** [[00:51:13](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3073)]
No, no, no, no, no.

##### **Geohot** [[00:51:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3074)]
It's all gone.

##### **Geohot** [[00:51:15](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3075)]
It's all gone.

##### **Geohot** [[00:51:15](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3075)]
As soon as you have one, you throw it all away.

##### **Geohot** [[00:51:17](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3077)]
So, but this isn't leaking abstractions.

##### **Chenyu** [[00:51:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3079)]
This is simply letting you tap into the entire abstraction stack.

##### **Geohot** [[00:51:24](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3084)]
We have the same philosophy at Comma about hardware.

##### **Geohot** [[00:51:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3087)]
I say that I want to sell all the intermediates, right?

##### **Geohot** [[00:51:30](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3090)]
If we use, if we use jungles to, to bring up Comma devices,

##### **Geohot** [[00:51:34](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3094)]
we sell jungles, right?

##### **Geohot** [[00:51:35](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3095)]
Like sell that.

##### **Chenyu** [[00:51:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3096)]
Turn it into a product, right?

##### **Geohot** [[00:51:38](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3098)]
For every one of our APIs that we can effectively turn into a

##### **Geohot** [[00:51:41](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3101)]
product that's an intermediate and tiny grad, it'll be better.

##### **Geohot** [[00:51:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3105)]
It'll be better because we had to put some polish on it to

##### **Geohot** [[00:51:47](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3107)]
productize it.

##### **Geohot** [[00:51:48](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3108)]
Now, you shouldn't productize it.

##### **Chenyu** [[00:51:49](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3109)]
Productize things too early, right?

##### **Geohot** [[00:51:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3111)]
If things are going to rapidly change, sure.

##### **Geohot** [[00:51:53](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3113)]
All the effort put into making this product is a waste, but I

##### **Geohot** [[00:51:57](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3117)]
don't think that the custom kernel syntax is going to change

##### **Geohot** [[00:52:02](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3122)]
too much.

##### **Geohot** [[00:52:04](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3124)]
You think it's going to change a lot?

##### **Chenyu** [[00:52:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3126)]
I don't know.

##### **Geohot** [[00:52:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3127)]
I mean, this thing is hard to predict.

##### **Geohot** [[00:52:10](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3130)]
Well, because many things have changed and it's very annoying

##### **Geohot** [[00:52:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3134)]
when I was bicycling stuff with my custom kernel to the previous

##### **Geohot** [[00:52:18](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3138)]
ones.

##### **Geohot** [[00:52:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3139)]
Yeah.

##### **Chenyu** [[00:52:20](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3140)]
I mean, sure.

##### **Geohot** [[00:52:20](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3140)]
I think that syntactically it's going to change.

##### **Geohot** [[00:52:23](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3143)]
It's not like 1.0 syntactically, but I'm not like, it's hard for me

##### **Geohot** [[00:52:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3147)]
to imagine where you'd have to add, like, think about the device

##### **Geohot** [[00:52:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3156)]
abstraction and think about the last time that changed.

##### **Geohot** [[00:52:39](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3159)]
It used to change a lot.

##### **Chenyu** [[00:52:43](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3163)]
When's the last time it changed?

##### **Geohot** [[00:52:47](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3167)]
The competitor pair or something?

##### **Geohot** [[00:52:48](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3168)]
The device pair or something?

##### **Geohot** [[00:52:49](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3169)]
Like, it should change.

##### **Geohot** [[00:52:50](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3170)]
Shiny change.

##### **Geohot** [[00:52:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3172)]
It's pretty much not that.

##### **Chenyu** [[00:52:53](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3173)]
More of a minor annoyance.

##### **Geohot** [[00:52:55](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3175)]
I mean, similar to tracking what happened to the handwritten syntax,

##### **Geohot** [[00:53:02](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3182)]
yes, it's minor annoyance.

##### **Geohot** [[00:53:03](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3183)]
Yeah.

##### **Geohot** [[00:53:04](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3184)]
Can you write a custom backward function?

##### **Geohot** [[00:53:05](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3185)]
Yeah.

##### **Chenyu** [[00:53:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3186)]
You can write a custom backward function and you can use custom

##### **Geohot** [[00:53:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3188)]
kernel in it.

##### **Geohot** [[00:53:09](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3189)]
See examples in test slash test underscore custom kernels.

##### **Geohot** [[00:53:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3194)]
There are a few, I think just one, backward examples, but that should

##### **Geohot** [[00:53:18](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3198)]
be enough to.

##### **Geohot** [[00:53:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3199)]
For you to get started.

##### **Chenyu** [[00:53:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3207)]
Sorry, you want to say something?

##### **Geohot** [[00:53:29](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3209)]
No, but I, you know, I'll just start working on the contract.

##### **Geohot** [[00:53:39](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3219)]
Okay.

##### **Geohot** [[00:53:41](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3221)]
Do we have any other bounty?

##### **Geohot** [[00:53:42](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3222)]
I don't think so.

##### **Geohot** [[00:53:47](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3227)]
PH with limit here.

##### **Chenyu** [[00:53:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3231)]
Bounce, bounce, bounce.

##### **Geohot** [[00:53:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3231)]
Very bad, bro.

##### **Geohot** [[00:53:55](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3235)]
So quite layered.

##### **Geohot** [[00:53:56](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3236)]
Really, very different, just weird versatility.

##### **Geohot** [[00:54:02](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3242)]
I feel that we have a few of our Imperial bases in and all that.

##### **Geohot** [[00:54:03](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3243)]
I'll pass that to that guy.

##### **Chenyu** [[00:54:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3246)]
Does that make, the hanover bordermule copper,

##### **Geohot** [[00:54:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3248)]
which really Mahloum Singkhe is lasers sister.

##### **Geohot** [[00:54:09](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3249)]
Have you gotory spell stuck,

##### **Geohot** [[00:54:09](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3249)]
you should, which is in situ.

##### **Geohot** [[00:54:10](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3250)]
No, you just do VEC.

##### **Geohot** [[00:54:11](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3251)]
Every day there's randomized updates.

##### **Chenyu** [[00:54:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3252)]
More or less.

##### **Geohot** [[00:54:15](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3255)]
Speaking of this, someone raised another issue saying your change made some accounts lower.

##### **Geohot** [[00:54:21](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3261)]
Probably did.

##### **Geohot** [[00:54:24](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3264)]
Okay.

##### **Geohot** [[00:54:25](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3265)]
We can't do anything about that.

##### **Geohot** [[00:54:29](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3269)]
Like, I made it slower, great. Like, long term, there's a few approaches here. But the real

##### **Chenyu** [[00:54:38](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3278)]
approach, the reason things get slower is because you've increased register pressure. Your order of

##### **Geohot** [[00:54:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3285)]
your instructions determines register pressure. And LLVM is not that good at reordering things

##### **Geohot** [[00:54:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3291)]
to alleviate register pressure. So, yeah. What you want to do is you want to write a register

##### **Geohot** [[00:55:03](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3303)]
allocator. And then even if you are going to output it,

##### **Geohot** [[00:55:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3308)]
to C, which is going to be re-register allocated, putting it in an order that minimizes register

##### **Geohot** [[00:55:13](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3313)]
pressure is going to give you faster kernels. So, that's probably why the speed changes.

##### **Chenyu** [[00:55:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3319)]
With respect to, like, is TinyGrad going to have the fastest convs? Not in six months.

##### **Geohot** [[00:55:26](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3326)]
It has the fastest convs on Snapdragon 845.

##### **Geohot** [[00:55:33](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3333)]
Literally almost no matter how much you regress them, they'll be faster than SMPEs.

##### **Geohot** [[00:55:38](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3338)]
But, yeah, I mean, no. There's no.. If someone wants to pay me $1.6 million for fast convs,

##### **Geohot** [[00:55:44](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3344)]
I will write fast convs. And that's, like, go where the money is. Not because we need the money,

##### **Geohot** [[00:55:50](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3350)]
but because if someone's willing to pay for it, it's useful.

##### **Chenyu** [[00:55:55](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3355)]
You don't think there's some chance that.. Like, what percent chance is it worth it if we end up

##### **Geohot** [[00:56:01](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3361)]
replacing AMD's entire stack? Oh, chance?

##### **Geohot** [[00:56:05](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3365)]
Yeah, what do you think our chances of doing that are?

##### **Geohot** [[00:56:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3367)]
Yeah.

##### **Geohot** [[00:56:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3368)]
Why so low?

##### **Geohot** [[00:56:10](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3370)]
I mean, you ask. I give you a number.

##### **Chenyu** [[00:56:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3372)]
No, why do you think it's so low?

##### **Geohot** [[00:56:15](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3375)]
I'm willing to pay $1,000 to $1.

##### **Geohot** [[00:56:18](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3378)]
Versus AMD?

##### **Geohot** [[00:56:20](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3380)]
Yeah.

##### **Geohot** [[00:56:21](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3381)]
I would give us $1,000 to $1 versus Nvidia.

##### **Geohot** [[00:56:24](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3384)]
Nvidia is probably even lower.

##### **Chenyu** [[00:56:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3387)]
But why do you think AMD is so low? Have you used their stack?

##### **Geohot** [[00:56:31](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3391)]
No.

##### **Geohot** [[00:56:32](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3392)]
Try it.

##### **Geohot** [[00:56:33](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3393)]
Oh.

##### **Geohot** [[00:56:34](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3394)]
Try using AMD on anything besides TinyGrad.

##### **Geohot** [[00:56:39](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3399)]
And it works right up until it doesn't.

##### **Chenyu** [[00:56:42](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3402)]
Right? Sure. The GEMM and torch is faster.

##### **Geohot** [[00:56:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3405)]
No. I mean, that doesn't change my impression for this probability estimation.

##### **Geohot** [[00:56:49](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3409)]
Why?

##### **Geohot** [[00:56:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3411)]
Because it's not about that.

##### **Geohot** [[00:56:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3412)]
What is it about?

##### **Geohot** [[00:56:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3414)]
I don't know.

##### **Chenyu** [[00:56:55](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3415)]
But, like, why do you think it's low?

##### **Geohot** [[00:56:57](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3417)]
Well, I mean, it's 0.1%.

##### **Geohot** [[00:56:59](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3419)]
Yeah, but why do you..

##### **Geohot** [[00:57:00](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3420)]
It's pretty high.

##### **Geohot** [[00:57:02](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3422)]
Okay. So, I mean, someone's gonna.. Or.. Okay.

##### **Geohot** [[00:57:05](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3425)]
So, let's just start.

##### **Chenyu** [[00:57:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3427)]
Let's start with not AMD using this.

##### **Geohot** [[00:57:13](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3433)]
What do you mean, not AMD?

##### **Geohot** [[00:57:15](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3435)]
I mean, I don't see how this would happen.

##### **Geohot** [[00:57:18](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3438)]
What do you mean?

##### **Geohot** [[00:57:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3439)]
How what?

##### **Geohot** [[00:57:20](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3440)]
Oh, AMD replaced the full stack with TinyGrad?

##### **Chenyu** [[00:57:24](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3444)]
Well, okay, so..

##### **Geohot** [[00:57:25](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3445)]
That's why you asked, right?

##### **Geohot** [[00:57:26](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3446)]
The probability of that happening.

##### **Geohot** [[00:57:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3447)]
No, the probability of TinyGrad being the dominant used stack on AMD.

##### **Geohot** [[00:57:31](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3451)]
I'm not saying for AMD internally to cancel RockAM.

##### **Geohot** [[00:57:34](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3454)]
Oh, you mean for people to use TinyGrad on AMD?

##### **Chenyu** [[00:57:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3456)]
Yeah.

##### **Geohot** [[00:57:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3457)]
But that TinyGrad is the go-to stack for AMD.

##### **Geohot** [[00:57:40](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3460)]
That's pretty low.

##### **Geohot** [[00:57:42](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3462)]
Why?

##### **Geohot** [[00:57:44](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3464)]
That's my impression.

##### **Geohot** [[00:57:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3465)]
What do you think the go-to stack on AMD will be?

##### **Chenyu** [[00:57:50](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3470)]
Oh..

##### **Geohot** [[00:57:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3474)]
I don't know.

##### **Geohot** [[00:57:59](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3479)]
It's gonna be something, right?

##### **Geohot** [[00:58:01](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3481)]
Yes.

##### **Geohot** [[00:58:02](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3482)]
So, do you think it's gonna be their RockAM Torch stack?

##### **Geohot** [[00:58:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3487)]
I don't know.

##### **Chenyu** [[00:58:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3487)]
I don't know.

##### **Geohot** [[00:58:10](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3490)]
But you are the fact-checking

##### **Geohot** [[00:58:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3492)]
I mean, for the price, of course.

##### **Geohot** [[00:58:15](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3495)]
Yeah, but then you have the..

##### **Geohot** [[00:58:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3499)]
You have the first multiple points as well, first match, followed up

##### **Geohot** [[00:58:20](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3500)]
You have the Sc crews, the V- dishwasher, you have dobre A's.

##### **Chenyu** [[00:58:23](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3503)]
Right.

##### **Geohot** [[00:58:24](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3504)]
So, I'm not saying you bought that stack..

##### **Geohot** [[00:58:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3507)]
You bought it on Axes, right?

##### **Geohot** [[00:58:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3507)]
You paid Rs 300,000 to solve the problem,

##### **Geohot** [[00:58:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3507)]
You paid between Rs 300,000 and 20,500?

##### **Geohot** [[00:58:30](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3510)]
Close.

##### **Chenyu** [[00:58:31](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3511)]
Jax.

##### **Geohot** [[00:58:32](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3512)]
Jax.

##### **Geohot** [[00:58:34](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3514)]
You think there's a 70% chance

##### **Geohot** [[00:58:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3516)]
that somehow they're going to hack together

##### **Geohot** [[00:58:38](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3518)]
the PyTorch stack?

##### **Geohot** [[00:58:39](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3519)]
There's a 29.9% chance that Google

##### **Chenyu** [[00:58:42](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3522)]
is somehow going to fix all their stuff

##### **Geohot** [[00:58:44](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3524)]
and care remotely about AMD GPU.

##### **Geohot** [[00:58:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3532)]
No, it's not about that.

##### **Geohot** [[00:58:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3534)]
It's about what user would choose,

##### **Geohot** [[00:58:56](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3536)]
which framework when they have AMD hardware.

##### **Geohot** [[00:58:59](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3539)]
Do you think they are going to choose Tiny?

##### **Chenyu** [[00:59:01](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3541)]
Do you think they are going to choose Torch, Jax?

##### **Geohot** [[00:59:04](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3544)]
That's our problem, right?

##### **Geohot** [[00:59:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3546)]
The question was,

##### **Geohot** [[00:59:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3548)]
now the user bought or have AMD hardware,

##### **Geohot** [[00:59:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3552)]
how are they going to choose which framework to use?

##### **Geohot** [[00:59:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3554)]
They're going to try all three.

##### **Chenyu** [[00:59:18](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3558)]
I don't even know that's true to start with, but sure.

##### **Geohot** [[00:59:21](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3561)]
What do you mean?

##### **Geohot** [[00:59:24](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3564)]
You don't think they're going to try all three?

##### **Geohot** [[00:59:26](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3566)]
No.

##### **Geohot** [[00:59:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3567)]
What do you think they're going to try?

##### **Geohot** [[00:59:29](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3569)]
They're going to try all three.

##### **Chenyu** [[00:59:29](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3569)]
Oh, Torch.

##### **Geohot** [[00:59:31](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3571)]
Okay, what are they going to do

##### **Geohot** [[00:59:32](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3572)]
when they hit bugs in Torch?

##### **Geohot** [[00:59:34](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3574)]
Similar to what they're going to do

##### **Geohot** [[00:59:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3577)]
when they hit bugs in TinyGrad.

##### **Geohot** [[00:59:39](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3579)]
It's not like we care that much about fixing user bugs.

##### **Chenyu** [[00:59:41](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3581)]
No, no, no.

##### **Geohot** [[00:59:42](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3582)]
So you think people aren't going to try TinyGrad

##### **Geohot** [[00:59:43](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3583)]
or you think people aren't going to,

##### **Geohot** [[00:59:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3585)]
or TinyGrad's not going to,

##### **Geohot** [[00:59:48](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3588)]
like they're going to hit too many bugs with it

##### **Geohot** [[00:59:50](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3590)]
or it's going to be too slow?

##### **Chenyu** [[00:59:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3592)]
It's very hard to predict in five years.

##### **Geohot** [[00:59:56](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3596)]
Let's just say three.

##### **Geohot** [[00:59:57](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3597)]
I mean, I think five's a little far.

##### **Geohot** [[00:59:59](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3599)]
Oh, three, then we just see.

##### **Geohot** [[01:00:04](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3604)]
I think people will hopefully try it.

##### **Geohot** [[01:00:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3606)]
I give TinyGrad easily a 20% chance

##### **Chenyu** [[01:00:09](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3609)]
of being the dominant stack in three years on AMD.

##### **Geohot** [[01:00:15](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3615)]
And I give us a 0.1% chance

##### **Geohot** [[01:00:17](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3617)]
of being the dominant stack on Nvidia.

##### **Geohot** [[01:00:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3619)]
Okay.

##### **Geohot** [[01:00:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3619)]
But I don't understand.

##### **Geohot** [[01:00:21](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3621)]
If you don't believe that, why do you work here?

##### **Chenyu** [[01:00:24](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3624)]
No, I mean, because I don't think

##### **Geohot** [[01:00:26](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3626)]
that's the important thing for the company.

##### **Geohot** [[01:00:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3627)]
Well, what's the important thing?

##### **Geohot** [[01:00:30](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3630)]
I don't know.

##### **Geohot** [[01:00:31](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3631)]
There's a chance.

##### **Geohot** [[01:00:34](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3634)]
I want you to try the AMD stuff.

##### **Chenyu** [[01:00:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3637)]
Like, go try it.

##### **Geohot** [[01:00:41](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3641)]
Does it run ResNet?

##### **Geohot** [[01:00:43](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3643)]
Maybe.

##### **Geohot** [[01:00:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3645)]
Can it run ResNet training?

##### **Geohot** [[01:00:47](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3647)]
Maybe the problem is I am not a target user

##### **Geohot** [[01:00:49](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3649)]
to train things on this model.

##### **Chenyu** [[01:00:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3651)]
I train it now because I need to train things on it.

##### **Geohot** [[01:00:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3654)]
So I don't have the motivation to figure out

##### **Geohot** [[01:00:56](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3656)]
what's the best to train things on it.

##### **Geohot** [[01:00:58](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3658)]
So, I mean, the question,

##### **Geohot** [[01:00:58](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3658)]
the question to ask isn't, like,

##### **Geohot** [[01:01:00](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3660)]
for Comma switching their training to TinyGrad on Nvidia,

##### **Chenyu** [[01:01:03](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3663)]
that's a really high bar.

##### **Geohot** [[01:01:05](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3665)]
Yeah, but if we don't even have a path to that,

##### **Geohot** [[01:01:10](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3670)]
then what's the point?

##### **Geohot** [[01:01:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3672)]
We don't have to.

##### **Geohot** [[01:01:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3674)]
Then who's going to use it if we're not going to use it?

##### **Geohot** [[01:01:16](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3676)]
Who's using MLX?

##### **Chenyu** [[01:01:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3679)]
I don't know.

##### **Geohot** [[01:01:20](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3680)]
People seem to run inference on their Mac happily.

##### **Geohot** [[01:01:22](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3682)]
I use MLX.

##### **Geohot** [[01:01:23](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3683)]
There you go.

##### **Geohot** [[01:01:24](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3684)]
Yeah.

##### **Geohot** [[01:01:25](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3685)]
It's just the same thing.

##### **Chenyu** [[01:01:29](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3689)]
What percent chance do you give MLX

##### **Geohot** [[01:01:31](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3691)]
of being the dominant framework on Apple in three years?

##### **Geohot** [[01:01:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3696)]
It's that low?

##### **Geohot** [[01:01:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3697)]
Yeah, of course.

##### **Geohot** [[01:01:38](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3698)]
No way.

##### **Geohot** [[01:01:40](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3700)]
What do you think?

##### **Chenyu** [[01:01:41](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3701)]
They already give up.

##### **Geohot** [[01:01:43](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3703)]
MLX has given up?

##### **Geohot** [[01:01:44](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3704)]
Yeah.

##### **Geohot** [[01:01:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3705)]
Really?

##### **Geohot** [[01:01:46](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3706)]
That's why they pivot to CUDA.

##### **Geohot** [[01:01:49](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3709)]
MLX is trying.

##### **Chenyu** [[01:01:50](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3710)]
No, MLX is just adding a CUDA back in.

##### **Geohot** [[01:01:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3712)]
Yeah.

##### **Geohot** [[01:01:53](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3713)]
And they are trying all their resources on that.

##### **Geohot** [[01:01:55](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3715)]
Well, no, but that's why.

##### **Geohot** [[01:01:57](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3717)]
What do you mean?

##### **Geohot** [[01:01:58](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3718)]
Because they want MLX to be the one-stop shop.

##### **Chenyu** [[01:02:03](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3723)]
Okay.

##### **Geohot** [[01:02:04](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3724)]
MLX people are basically betting on all developers have Apple.

##### **Geohot** [[01:02:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3727)]
But then sometimes you run it in the data center on CUDA,

##### **Geohot** [[01:02:10](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3730)]
so we want the same MLX code to run in both places.

##### **Geohot** [[01:02:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3732)]
Yeah.

##### **Geohot** [[01:02:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3732)]
Two percent.

##### **Chenyu** [[01:02:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3734)]
For on Mac?

##### **Geohot** [[01:02:15](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3735)]
Yeah.

##### **Geohot** [[01:02:16](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3736)]
Come on, that's way higher.

##### **Geohot** [[01:02:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3739)]
I don't know.

##### **Geohot** [[01:02:20](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3740)]
Everyone has a number.

##### **Geohot** [[01:02:22](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3742)]
So what do you think the dominant thing is going to be on Mac?

##### **Chenyu** [[01:02:24](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3744)]
Torch?

##### **Geohot** [[01:02:25](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3745)]
Yeah, whatever Curvy is, I think it's Torch.

##### **Geohot** [[01:02:28](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3748)]
A lot of these things aren't even Torch.

##### **Geohot** [[01:02:30](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3750)]
A lot of these, these, these, uh, uh, G GML V LLM.

##### **Geohot** [[01:02:35](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3755)]
They're not Torch.

##### **Geohot** [[01:02:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3756)]
They're just the hand-coded kernel.

##### **Chenyu** [[01:02:38](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3758)]
Yeah.

##### **Geohot** [[01:02:39](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3759)]
Maybe part of that, but that's not a full framework.

##### **Geohot** [[01:02:43](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3763)]
Yeah.

##### **Geohot** [[01:02:43](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3763)]
But I want to compete there too.

##### **Geohot** [[01:02:48](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3768)]
Yep.

##### **Geohot** [[01:02:49](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3769)]
Oh, see, I think, I think that is easier than everyone.

##### **Chenyu** [[01:02:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3774)]
What do you mean on which?

##### **Geohot** [[01:02:56](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3776)]
The.

##### **Geohot** [[01:02:57](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3777)]
The ones that runs inference kernels on Mac.

##### **Geohot** [[01:03:00](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3780)]
I think we are kind of already winning at front.

##### **Geohot** [[01:03:03](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3783)]
Oh, see the problem with that.

##### **Geohot** [[01:03:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3786)]
I think the problem with the, the run inference kernels is you'd have to be,

##### **Chenyu** [[01:03:13](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3793)]
these things aren't good.

##### **Geohot** [[01:03:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3794)]
They're just easy.

##### **Geohot** [[01:03:18](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3798)]
Like these, these run inference kernels, things like O LLaMA.

##### **Geohot** [[01:03:21](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3801)]
Yeah.

##### **Geohot** [[01:03:21](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3801)]
O LLaMA is not good.

##### **Geohot** [[01:03:22](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3802)]
Yeah.

##### **Chenyu** [[01:03:23](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3803)]
They are not good, but they are good enough.

##### **Geohot** [[01:03:25](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3805)]
And.

##### **Geohot** [[01:03:25](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3805)]
I think most of the time.

##### **Geohot** [[01:03:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3807)]
Being good enough decides what would be the dominate from work on certain

##### **Geohot** [[01:03:31](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3811)]
power on certain tasks.

##### **Geohot** [[01:03:33](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3813)]
I think O LLaMA, their strength is in their distribution and packaging.

##### **Chenyu** [[01:03:40](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3820)]
And that's what dominates.

##### **Geohot** [[01:03:43](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3823)]
Let's decide like what's the dominate from work.

##### **Geohot** [[01:03:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3825)]
That's like Torch.

##### **Geohot** [[01:03:46](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3826)]
Torch is not the best.

##### **Geohot** [[01:03:48](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3828)]
Anything.

##### **Geohot** [[01:03:49](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3829)]
No, but I think that like you have a different target audience, right?

##### **Chenyu** [[01:03:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3832)]
I think O LLaMA is downloaded by like the, the, the, the kid who heard about.

##### **Geohot** [[01:03:57](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3837)]
AI who can't code.

##### **Geohot** [[01:03:58](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3838)]
He's like, I'll get AI to do my homework.

##### **Geohot** [[01:04:00](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3840)]
O LLaMA.

##### **Geohot** [[01:04:01](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3841)]
Yeah.

##### **Geohot** [[01:04:02](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3842)]
Right.

##### **Chenyu** [[01:04:02](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3842)]
But let's, let's, that's how the dominate software happens, right?

##### **Geohot** [[01:04:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3848)]
It's like people download trash things, but they still happy with it.

##### **Geohot** [[01:04:13](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3853)]
Uh, I don't think this is how the dominant software happens.

##### **Geohot** [[01:04:17](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3857)]
I'll give an example, right?

##### **Geohot** [[01:04:18](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3858)]
Like, like Napster and Kazaa are gone.

##### **Geohot** [[01:04:20](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3860)]
BitTorrent still exists.

##### **Chenyu** [[01:04:24](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3864)]
Every kid who wanted a pirate.

##### **Geohot** [[01:04:26](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3866)]
Eminem albums downloaded map star.

##### **Geohot** [[01:04:30](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3870)]
It's gone.

##### **Geohot** [[01:04:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3876)]
Um, no, I mean, I, I think, and then, and then if you want to, if you want to, do you want, you want, you want to give us something of being a, you want an 80% chance of being the dominant framework on something in three years?

##### **Geohot** [[01:04:46](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3886)]
10 store.

##### **Geohot** [[01:04:47](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3887)]
If we pivoted to 10 store tomorrow, I guarantee we could crush what they have.

##### **Chenyu** [[01:04:55](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3895)]
Exactly.

##### **Geohot** [[01:04:56](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3896)]
Yeah.

##### **Geohot** [[01:04:56](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3896)]
And that's why we do AMD.

##### **Geohot** [[01:05:00](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3900)]
Um, no, I also think it's kind of, uh, your success is then tied to 10 store and success, which already take you in these success.

##### **Geohot** [[01:05:09](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3909)]
Yeah.

##### **Geohot** [[01:05:09](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3909)]
Our success.

##### **Chenyu** [[01:05:10](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3910)]
That's a good boat to be on.

##### **Geohot** [[01:05:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3912)]
Is it?

##### **Geohot** [[01:05:13](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3913)]
Yeah.

##### **Geohot** [[01:05:13](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3913)]
I did $400,000.

##### **Geohot** [[01:05:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3919)]
Yeah.

##### **Geohot** [[01:05:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3919)]
Yeah.

##### **Chenyu** [[01:05:20](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3920)]
Yeah.

##### **Geohot** [[01:05:20](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3920)]
Yeah.

##### **Geohot** [[01:05:21](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3921)]
The AMD success is a good boat to be on.

##### **Geohot** [[01:05:24](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3924)]
I'm happy to tie ourselves to AMD.

##### **Geohot** [[01:05:29](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3929)]
You don't think AMD, you think AMD is going to fail?

##### **Geohot** [[01:05:32](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3932)]
Do you think Google is going to fail?

##### **Chenyu** [[01:05:35](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3935)]
No.

##### **Geohot** [[01:05:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3936)]
I think Google is actually more successful than AMD.

##### **Geohot** [[01:05:39](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3939)]
I think Nvidia and Google are like real winners in AI.

##### **Geohot** [[01:05:42](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3942)]
I think like Cranium is going to fail.

##### **Geohot** [[01:05:46](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3946)]
I think Elon's actually going to end up succeeding.

##### **Geohot** [[01:05:49](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3949)]
That's my bet.

##### **Chenyu** [[01:05:50](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3950)]
So that he's going to succeed.

##### **Geohot** [[01:05:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3952)]
Yes.

##### **Geohot** [[01:05:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3952)]
Yeah.

##### **Geohot** [[01:05:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3952)]
He's just too, oh, he cares about this too much.

##### **Geohot** [[01:05:55](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3955)]
He's going to succeed.

##### **Geohot** [[01:05:55](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3955)]
He's going to succeed.

##### **Chenyu** [[01:05:55](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3955)]
Yes.

##### **Geohot** [[01:05:56](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3956)]
So he'll get it.

##### **Geohot** [[01:05:57](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3957)]
He's slow.

##### **Geohot** [[01:05:58](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3958)]
He's slower at this than us, but he'll get it.

##### **Geohot** [[01:06:00](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3960)]
Yeah.

##### **Geohot** [[01:06:01](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3961)]
So I think that's the, that's a final boss.

##### **Chenyu** [[01:06:05](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3965)]
What do you mean?

##### **Geohot** [[01:06:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3966)]
Elon?

##### **Geohot** [[01:06:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3966)]
No, no.

##### **Geohot** [[01:06:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3967)]
The, the new coming ones, not the current ones.

##### **Geohot** [[01:06:11](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3971)]
So that's why.

##### **Geohot** [[01:06:13](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3973)]
Oh, well, no.

##### **Chenyu** [[01:06:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3974)]
I mean, I think Google is actually, I think Google is going to do really well.

##### **Geohot** [[01:06:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3979)]
Yeah.

##### **Geohot** [[01:06:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3979)]
And I think Jack's will support other things really well.

##### **Geohot** [[01:06:21](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3981)]
I don't.

##### **Geohot** [[01:06:22](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3982)]
Yeah.

##### **Geohot** [[01:06:22](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3982)]
But that's just the difference.

##### **Chenyu** [[01:06:24](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3984)]
Oh, you think Jack's is going to start selling?

##### **Geohot** [[01:06:25](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3985)]
I think he's going to start supporting GPUs really well.

##### **Geohot** [[01:06:26](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3986)]
Yeah.

##### **Geohot** [[01:06:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3987)]
I don't think so.

##### **Geohot** [[01:06:28](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3988)]
I think Google is going to figure out how to externalize their TPUs before they figure

##### **Geohot** [[01:06:31](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3991)]
out how to make Jack support GPUs.

##### **Chenyu** [[01:06:32](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3992)]
Why does Google want Jack to support GPUs?

##### **Geohot** [[01:06:35](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3995)]
Because they want to be like, Tommy, they have no work.

##### **Geohot** [[01:06:39](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=3999)]
But why don't they export their hardware?

##### **Geohot** [[01:06:41](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4001)]
They are also doing that.

##### **Geohot** [[01:06:43](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4003)]
Next you're going to tell me that CUDA is going to start supporting AMD GPUs.

##### **Geohot** [[01:06:49](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4009)]
So that's the difference.

##### **Chenyu** [[01:06:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4011)]
Why?

##### **Geohot** [[01:06:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4012)]
I don't know.

##### **Geohot** [[01:06:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4012)]
Who's going to work on that?

##### **Geohot** [[01:06:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4014)]
Who's going to work on making CUDA work on AMD GPUs?

##### **Geohot** [[01:06:58](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4018)]
Making Jack's work on AMD, on NVIDIA GPUs?

##### **Geohot** [[01:07:02](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4022)]
Do you think Google is going to put a concerted effort into making their framework work on

##### **Chenyu** [[01:07:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4027)]
their competitor?

##### **Geohot** [[01:07:10](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4030)]
It's not their competitor.

##### **Geohot** [[01:07:13](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4033)]
It exactly is their competitor.

##### **Geohot** [[01:07:17](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4037)]
I don't know.

##### **Geohot** [[01:07:18](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4038)]
Google, Google, if you're in Google Finance, you start looking around, you're like, how

##### **Geohot** [[01:07:22](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4042)]
the hell is NVIDIA worth more than us?

##### **Chenyu** [[01:07:23](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4043)]
We have a better AI chip than them.

##### **Geohot** [[01:07:28](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4048)]
In a lot of ways the TP was better.

##### **Geohot** [[01:07:32](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4052)]
It's just the normal things Google struggles with.

##### **Geohot** [[01:07:35](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4055)]
They struggle to actually like platformize these things.

##### **Geohot** [[01:07:40](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4060)]
But I think Google will figure it out.

##### **Geohot** [[01:07:42](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4062)]
Google is selling their chips to Anthropic.

##### **Chenyu** [[01:07:46](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4066)]
They're writing a low-level kernel interface for Anthropic.

##### **Geohot** [[01:07:48](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4068)]
This is all the palace stuff.

##### **Geohot** [[01:07:49](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4069)]
It's all open source.

##### **Geohot** [[01:07:50](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4070)]
They know the labs won't use it otherwise.

##### **Geohot** [[01:07:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4072)]
So I think Google is going to get in there and try to get a better AI chip.

##### **Geohot** [[01:07:53](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4073)]
Google is doing better at this.

##### **Chenyu** [[01:07:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4074)]
But I believe Google will sell TPUs long before JAX supports NVIDIA in a real way.

##### **Geohot** [[01:08:05](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4085)]
It kind of can't.

##### **Geohot** [[01:08:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4087)]
It's not really designed for that.

##### **Geohot** [[01:08:09](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4089)]
I mean, it would require some rethinking to their..

##### **Geohot** [[01:08:16](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4096)]
It's designed for things that look like TPU topologies.

##### **Geohot** [[01:08:21](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4101)]
Yeah.

##### **Chenyu** [[01:08:25](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4105)]
I see why that's very different.

##### **Geohot** [[01:08:28](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4108)]
NVIDIA has invested a ton of money now into making their switches to the AllReduce versus

##### **Geohot** [[01:08:35](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4115)]
the TPUs, which have to go in a ring.

##### **Geohot** [[01:08:38](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4118)]
Okay.

##### **Geohot** [[01:08:38](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4118)]
It's different.

##### **Geohot** [[01:08:40](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4120)]
Not that different.

##### **Chenyu** [[01:08:43](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4123)]
Just find another person working on this and it'll be fine.

##### **Geohot** [[01:08:47](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4127)]
No, but I think it's different enough.

##### **Geohot** [[01:08:48](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4128)]
I think it's almost like the difference between 10 store and GPUs.

##### **Geohot** [[01:08:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4132)]
The TPUs are different.

##### **Geohot** [[01:08:53](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4133)]
The GPU pod looks a lot like the 10 store car.

##### **Geohot** [[01:08:57](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4137)]
Whereas a GPU cluster looks a lot like a big GPU.

##### **Chenyu** [[01:09:03](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4143)]
So Elon's data center with the three big fans on top looks like a big..

##### **Geohot** [[01:09:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4147)]
Very big.

##### **Geohot** [[01:09:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4148)]
Very big.

##### **Geohot** [[01:09:09](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4149)]
He built the world's biggest GPU.

##### **Geohot** [[01:09:11](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4151)]
It's one GPU.

##### **Geohot** [[01:09:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4152)]
That's how NVIDIA wants you to think about this.

##### **Chenyu** [[01:09:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4154)]
I mean, Carmack was complaining that the software doesn't actually let you dispatch it like one GPU.

##### **Geohot** [[01:09:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4159)]
But it is one big GPU, really.

##### **Geohot** [[01:09:22](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4162)]
They're working on making..

##### **Geohot** [[01:09:23](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4163)]
Making the unified memory as big as possible.

##### **Geohot** [[01:09:26](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4166)]
They're fundamentally betting on the..

##### **Geohot** [[01:09:30](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4170)]
They're making the same bet that has historically won in computer architecture, which is people

##### **Chenyu** [[01:09:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4176)]
do not want..

##### **Geohot** [[01:09:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4177)]
Split stuff.

##### **Geohot** [[01:09:38](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4178)]
Split stuff.

##### **Geohot** [[01:09:39](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4179)]
Yeah.

##### **Geohot** [[01:09:40](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4180)]
Yeah.

##### **Geohot** [[01:09:41](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4181)]
So I think they're very different.

##### **Chenyu** [[01:09:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4185)]
I give us so much higher than 0.1% chance of being the dominant framework on AMD.

##### **Geohot** [[01:09:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4191)]
Okay.

##### **Geohot** [[01:09:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4191)]
Maybe 0.5%.

##### **Geohot** [[01:09:53](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4193)]
Maybe 0.5%.

##### **Geohot** [[01:09:53](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4193)]
But how about..

##### **Geohot** [[01:09:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4194)]
How about..

##### **Chenyu** [[01:09:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4194)]
How many people you think are going to start using USB GPUs?

##### **Geohot** [[01:10:00](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4200)]
If it works and Carmack can use it, then I will believe it.

##### **Geohot** [[01:10:04](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4204)]
Yes.

##### **Geohot** [[01:10:05](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4205)]
Yeah.

##### **Geohot** [[01:10:05](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4205)]
I mean, it's going to work.

##### **Geohot** [[01:10:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4207)]
Yeah.

##### **Chenyu** [[01:10:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4207)]
Yeah.

##### **Geohot** [[01:10:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4208)]
And there's more.

##### **Geohot** [[01:10:09](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4209)]
Well, they have to use TinyGraph for that.

##### **Geohot** [[01:10:11](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4211)]
Yes.

##### **Geohot** [[01:10:11](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4211)]
That's the problem.

##### **Geohot** [[01:10:13](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4213)]
But yes.

##### **Chenyu** [[01:10:13](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4213)]
I don't think that's a problem.

##### **Geohot** [[01:10:15](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4215)]
What do people want to do?

##### **Geohot** [[01:10:16](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4216)]
They want to run their LLM or their diffusion model on their Mac fast.

##### **Geohot** [[01:10:21](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4221)]
Yeah.

##### **Geohot** [[01:10:23](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4223)]
So they plug a 5090 in and they run it.

##### **Geohot** [[01:10:28](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4228)]
I think we can sell 10,000 of these.

##### **Chenyu** [[01:10:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4236)]
And then it forces people like, oh, I'm going to use TinyGraph.

##### **Geohot** [[01:10:42](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4242)]
If this hardware starts to exist, it forces people into our ecosystem.

##### **Geohot** [[01:10:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4252)]
Yeah.

##### **Geohot** [[01:10:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4252)]
Basically.

##### **Geohot** [[01:10:55](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4255)]
But all right.

##### **Geohot** [[01:10:55](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4255)]
So am I really doing the contract?

##### **Chenyu** [[01:10:56](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4256)]
You guys are not excited?

##### **Geohot** [[01:11:02](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4262)]
It's probably like, oh, you cannot do nothing as well as this, but not also.

##### **Geohot** [[01:11:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4266)]
But is that what you want me to work on?

##### **Geohot** [[01:11:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4268)]
I'm here to support the contract as best as I can.

##### **Geohot** [[01:11:10](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4270)]
What do you want me to work on?

##### **Geohot** [[01:11:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4274)]
I'm going to work on the contract.

##### **Chenyu** [[01:11:16](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4276)]
What I would do today is I would start looking into doing the memory layout.

##### **Geohot** [[01:11:21](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4281)]
And confirming that if we write stub custom kernels for flash attention, that the memory

##### **Geohot** [[01:11:29](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4289)]
usage is appropriate.

##### **Geohot** [[01:11:31](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4291)]
Yeah.

##### **Geohot** [[01:11:31](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4291)]
So that's what we are kind of already out there with.

##### **Geohot** [[01:11:32](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4292)]
Oh, you're doing it.

##### **Chenyu** [[01:11:34](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4294)]
Who's doing it?

##### **Geohot** [[01:11:34](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4294)]
I mean.

##### **Geohot** [[01:11:35](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4295)]
He's working on the kernels.

##### **Geohot** [[01:11:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4297)]
Yeah.

##### **Geohot** [[01:11:38](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4298)]
You would first need to have a kernel and look into them.

##### **Geohot** [[01:11:40](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4300)]
No, you don't.

##### **Chenyu** [[01:11:41](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4301)]
No, no.

##### **Geohot** [[01:11:41](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4301)]
Just write a stub kernel.

##### **Geohot** [[01:11:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4305)]
What do you mean?

##### **Geohot** [[01:11:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4305)]
Well, do you want me to do this or do you want to do it?

##### **Geohot** [[01:11:49](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4309)]
Well, that we can discuss that later.

##### **Geohot** [[01:11:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4311)]
Okay.

##### **Chenyu** [[01:11:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4311)]
No, I think, I mean, I think like a stub kernel.

##### **Geohot** [[01:11:54](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4314)]
Like you can, you can just stub out flash attention.

##### **Geohot** [[01:11:57](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4317)]
Even if it doesn't actually have the compute in there.

##### **Geohot** [[01:12:00](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4320)]
Just put a blank kernel.

##### **Geohot** [[01:12:03](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4323)]
Okay.

##### **Geohot** [[01:12:03](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4323)]
And then that will, the memory usage is not determined by anything inside your kernel.

##### **Chenyu** [[01:12:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4328)]
Okay.

##### **Geohot** [[01:12:09](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4329)]
So confirm that we can fit 8192 context length 405B on the MI355 box.

##### **Geohot** [[01:12:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4339)]
Uh, sure.

##### **Geohot** [[01:12:20](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4340)]
And then we can figure out what the kernels.

##### **Geohot** [[01:12:23](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4343)]
So the stub kernels are not going to actually train.

##### **Geohot** [[01:12:26](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4346)]
It's going to, it's going to NAD, but that's fine.

##### **Chenyu** [[01:12:29](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4349)]
We can get an idea of the timing.

##### **Geohot** [[01:12:31](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4351)]
We can get memory numbers and we can get, uh, syncing working.

##### **Geohot** [[01:12:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4357)]
Right.

##### **Geohot** [[01:12:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4357)]
We can do all of this in pieces now too.

##### **Geohot** [[01:12:42](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4362)]
I'll write, I'll write the stub kernel.

##### **Geohot** [[01:12:43](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4363)]
I'll do that.

##### **Chenyu** [[01:12:44](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4364)]
I don't have the common meetings next, but I'll write, I'll write the stub kernel and

##### **Geohot** [[01:12:47](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4367)]
kind of show what this is.

##### **Geohot** [[01:12:48](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4368)]
Okay.

##### **Geohot** [[01:12:48](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4368)]
It's just like, this is like an empty kernel.

##### **Geohot** [[01:12:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4372)]
Yeah.

##### **Geohot** [[01:12:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4372)]
But that should work, right?

##### **Chenyu** [[01:12:56](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4376)]
Well, yeah, but I'm, I don't know.

##### **Geohot** [[01:12:58](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4378)]
I don't know if like the memory for everything else is fine.

##### **Geohot** [[01:13:01](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4381)]
Is it just flash attention that's wasting all the memory?

##### **Geohot** [[01:13:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4386)]
Or do we have other problems?

##### **Geohot** [[01:13:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4387)]
Uh, there really are lots of other kernels there.

##### **Geohot** [[01:13:11](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4391)]
I don't know.

##### **Chenyu** [[01:13:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4392)]
I don't know.

##### **Geohot** [[01:13:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4392)]
It's going to be like the activation is saving everything twice.

##### **Geohot** [[01:13:15](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4395)]
We don't have gradient checkpointing.

##### **Geohot** [[01:13:17](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4397)]
Like that kind of stuff.

##### **Geohot** [[01:13:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4399)]
Yeah.

##### **Geohot** [[01:13:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4399)]
But that we also know that we need to implement.

##### **Chenyu** [[01:13:23](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4403)]
So.

##### **Geohot** [[01:13:23](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4403)]
Oh, well, but that's independent of custom kernels.

##### **Geohot** [[01:13:26](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4406)]
Yeah.

##### **Geohot** [[01:13:27](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4407)]
So, so, so what is the condition on that?

##### **Geohot** [[01:13:31](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4411)]
We probably already need to list.

##### **Geohot** [[01:13:33](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4413)]
I don't know what.

##### **Chenyu** [[01:13:34](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4414)]
We can work on a lot of this in parallel, right?

##### **Geohot** [[01:13:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4417)]
We can work on a lot of, so we can work on there.

##### **Geohot** [[01:13:41](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4421)]
I see, I really see four parts to this.

##### **Geohot** [[01:13:44](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4424)]
I see four parts for the four other people who work here.

##### **Geohot** [[01:13:46](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4426)]
There is the high level trainer part, which is running the trainer and like stubbing out each one of these parts.

##### **Geohot** [[01:13:57](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4437)]
And then the parts are that we need a flash attention and a GEMM kernel, forwards and backwards.

##### **Chenyu** [[01:14:03](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4443)]
There's the custom kernels.

##### **Geohot** [[01:14:04](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4444)]
There's the data movement, which is like, you know, when Illogen started to work on with the CPU offload, how fast is that CPU offload copy?

##### **Geohot** [[01:14:15](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4455)]
So there's, there's.

##### **Geohot** [[01:14:16](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4456)]
There's the driver part of it.

##### **Geohot** [[01:14:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4459)]
There is the kernel part of it actually writing those kernels.

##### **Geohot** [[01:14:23](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4463)]
And then there is the visualization to figure out how we can, why these kernels are slow and how we can make these kernels faster.

##### **Chenyu** [[01:14:29](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4469)]
Just, you know, take a look at this whole thing and figure out where the bottlenecks are.

##### **Geohot** [[01:14:32](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4472)]
Right.

##### **Geohot** [[01:14:32](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4472)]
It's these four things.

##### **Geohot** [[01:14:35](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4475)]
You know, look, I try my best to break this out into tasks.

##### **Geohot** [[01:14:38](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4478)]
And then I think that's the only four things.

##### **Geohot** [[01:14:40](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4480)]
I don't think there's more.

##### **Chenyu** [[01:14:43](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4483)]
But again, if there's anything else I can do to.

##### **Geohot** [[01:14:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4485)]
Yeah.

##### **Geohot** [[01:14:46](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4486)]
Then this, this leaves me open to support and I'll do whatever I'll do, whatever the worst grunt work is.

##### **Geohot** [[01:14:53](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4493)]
I don't know if like, you know, you're, you're frustrated with syntax of the custom kernels or you're frustrated with the Python speed or you're frustrated with the CI taking too long or whatever.

##### **Geohot** [[01:15:05](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4505)]
I'm frustrated with the OpenPy regression.

##### **Geohot** [[01:15:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4507)]
You want me to fix the OpenPy regression?

##### **Chenyu** [[01:15:09](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4509)]
I can do that.

##### **Geohot** [[01:15:09](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4509)]
You got the OpenPy regression.

##### **Geohot** [[01:15:11](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4511)]
Okay.

##### **Geohot** [[01:15:11](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4511)]
Yes.

##### **Geohot** [[01:15:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4512)]
You do the OpenPy regression.

##### **Geohot** [[01:15:13](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4513)]
I'll do the, the, the stub kernels.

##### **Chenyu** [[01:15:18](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4518)]
And with the stub kernels, we can kind of kick this off and we can actually look at each individual piece because I should be able to stop pretty much everything.

##### **Geohot** [[01:15:25](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4525)]
Oh, yeah.

##### **Geohot** [[01:15:26](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4526)]
I can run that with an L backend and see if these have something wrong.

##### **Geohot** [[01:15:30](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4530)]
Yeah.

##### **Geohot** [[01:15:30](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4530)]
We run this with an L backend and like, let's go for this.

##### **Geohot** [[01:15:32](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4532)]
Like, you know, you know, you know, you know what it was like looking at the DSP and being like, I got to do this in, I got to do this in 12 milliseconds.

##### **Chenyu** [[01:15:42](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4542)]
It's taking 1200 now.

##### **Geohot** [[01:15:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4545)]
I'm a hundred X off.

##### **Geohot** [[01:15:47](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4547)]
And every day it got a little bit faster and a little bit faster and a little bit faster.

##### **Geohot** [[01:15:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4551)]
And then it did it in 12.

##### **Geohot** [[01:15:55](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4555)]
And I would say that like, yeah, sure.

##### **Geohot** [[01:15:58](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4558)]
There was 30% of the DSP contract.

##### **Chenyu** [[01:15:59](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4559)]
We didn't end up merging.

##### **Geohot** [[01:16:01](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4561)]
But 70% is like all the fundamental base stuff now is there for the DSP.

##### **Geohot** [[01:16:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4568)]
And TVM doesn't have that.

##### **Geohot** [[01:16:11](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4571)]
TVM doesn't have that.

##### **Geohot** [[01:16:11](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4571)]
TVM has a, has a unmaintained terrible fork for the Qualcomm DSP because it's different.

##### **Geohot** [[01:16:16](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4576)]
Like the DSP was so valuable to do.

##### **Chenyu** [[01:16:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4579)]
I think the GPU is too.

##### **Geohot** [[01:16:20](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4580)]
And I think, I mean, yeah, these big data center GPUs, we should, you know, we should really just do what pays us money.

##### **Geohot** [[01:16:29](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4589)]
But we should really do, we should really like, I really liked it.

##### **Geohot** [[01:16:34](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4594)]
This one pays us money because it's worth it to somebody, right?

##### **Geohot** [[01:16:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4597)]
That's providing value for other people.

##### **Geohot** [[01:16:40](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4600)]
But I cool.

##### **Chenyu** [[01:16:42](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4602)]
All right.

##### **Geohot** [[01:16:42](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4602)]
That stops today.

##### **Geohot** [[01:16:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4605)]
Yeah.

##### **Geohot** [[01:16:47](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4607)]
Don't, Qazalin, don't get too hung up on the, if the reverse engineering stuff's annoying, I can take a look at it.

##### **Geohot** [[01:16:56](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4616)]
Just like parsing out the binary format.

##### **Geohot** [[01:16:58](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4618)]
I'm very good at that.

##### **Chenyu** [[01:17:01](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4621)]
But yeah, no, I mean, we want to just, we want to just match the tools we have.

##### **Geohot** [[01:17:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4626)]
And then, no, no, no.

##### **Geohot** [[01:17:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4628)]
No.

##### **Geohot** [[01:17:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4628)]
No.

##### **Geohot** [[01:17:09](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4629)]
No.

##### **Geohot** [[01:17:09](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4629)]
Then what's in, did you ever get stuff up and working for testing all the copy to CPU?

##### **Chenyu** [[01:17:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4634)]
She'll be fast.

##### **Geohot** [[01:17:22](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4642)]
It is fast, but yeah.

##### **Geohot** [[01:17:28](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4648)]
Yeah.

##### **Geohot** [[01:17:29](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4649)]
I mean, we might have to, what'd he say?

##### **Geohot** [[01:17:32](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4652)]
When it's craft.

##### **Geohot** [[01:17:36](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4656)]
When it's.

##### **Chenyu** [[01:17:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4657)]
Yeah, because, I mean, when it's craft, it's fast.

##### **Geohot** [[01:17:41](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4661)]
It's full PCI speed.

##### **Geohot** [[01:17:43](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4663)]
When it's inside graph, I mean.

##### **Geohot** [[01:17:46](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4666)]
Oh, when it's graphed.

##### **Geohot** [[01:17:47](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4667)]
Oh, yeah.

##### **Geohot** [[01:17:48](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4668)]
Yeah.

##### **Chenyu** [[01:17:48](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4668)]
Yeah.

##### **Geohot** [[01:17:49](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4669)]
We'll check that.

##### **Geohot** [[01:17:50](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4670)]
I mean, I think we're going to have to do better all reduces to, like, I think the all reduce right now is, like, we can, it's all a unified memory space, effectively.

##### **Geohot** [[01:18:02](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4682)]
We have, all we do is using the DMA engine, but we don't use the DMA engine.

##### **Geohot** [[01:18:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4686)]
I don't think we need that level of overlapping to get it, but we'll see.

##### **Geohot** [[01:18:10](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4690)]
All right, cool.

##### **Chenyu** [[01:18:10](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4690)]
I'll just dump stuff today.

##### **Geohot** [[01:18:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4692)]
And then we can kind of see what the individual pieces are going to have to be.

##### **Geohot** [[01:18:16](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4696)]
But yeah, I think we should be able to have something training by the end of the year.

##### **Geohot** [[01:18:19](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4699)]
I think we should have stuff that's pretty close to state of the art GEMM and flash attention on the MI325X.

##### **Geohot** [[01:18:25](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4705)]
And then we can push to things like, has anyone submitted FPA stuff?

##### **Geohot** [[01:18:30](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4710)]
Have you got any FPA stuff yet?

##### **Chenyu** [[01:18:33](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4713)]
Oh, I don't know.

##### **Geohot** [[01:18:34](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4714)]
Is it out?

##### **Geohot** [[01:18:35](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4715)]
I think they released the new training stuff, but.

##### **Geohot** [[01:18:39](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4719)]
Oh, they have to, because last week I checked it's not out yet.

##### **Geohot** [[01:18:43](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4723)]
Oh, it's not out yet.

##### **Geohot** [[01:18:43](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4723)]
Okay.

##### **Chenyu** [[01:18:43](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4723)]
Oh, you mean, oh, yeah, yeah, yeah.

##### **Geohot** [[01:18:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4725)]
I'm curious.

##### **Geohot** [[01:18:45](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4725)]
Because we did submit, so we are not able to see you on our submission.

##### **Geohot** [[01:18:49](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4729)]
Oh, I see.

##### **Geohot** [[01:18:50](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4730)]
Okay.

##### **Geohot** [[01:18:50](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4730)]
Okay.

##### **Chenyu** [[01:18:51](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4731)]
Well, yeah, yeah.

##### **Geohot** [[01:18:52](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4732)]
When that comes out, we'll see.

##### **Geohot** [[01:18:53](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4733)]
I hope someone did FPA and we can just match FPA because that's why I got a number put in the contract and not a, because we get FPA, I think we hit all four of them.

##### **Geohot** [[01:19:03](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4743)]
Get our $1.6 million.

##### **Geohot** [[01:19:04](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4744)]
And then I give us easily a 20% chance in three years for being the dominant framework on AMD.

##### **Geohot** [[01:19:11](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4751)]
Three?

##### **Chenyu** [[01:19:12](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4752)]
Easy.

##### **Geohot** [[01:19:13](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4753)]
Off the AMD.

##### **Geohot** [[01:19:14](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4754)]
No, you really don't think this is, you'd really, you'd, wait, wait, wait.

##### **Geohot** [[01:19:18](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4758)]
No, no, no.

##### **Geohot** [[01:19:18](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4758)]
Would you take a bet at 1,000 to one?

##### **Geohot** [[01:19:24](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4764)]
I'm the one who can change this so much.

##### **Chenyu** [[01:19:31](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4771)]
I'm just an insider.

##### **Geohot** [[01:19:33](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4773)]
No, but there's no way it's 1,000 to one.

##### **Geohot** [[01:19:34](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4774)]
There's no way.

##### **Geohot** [[01:19:37](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4777)]
Because you have the energy to make that number higher.

##### **Geohot** [[01:19:41](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4781)]
But it shouldn't be my energy.

##### **Geohot** [[01:19:43](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4783)]
We have to just succeed at this technical problem.

##### **Chenyu** [[01:19:47](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4787)]
Yeah.

##### **Geohot** [[01:19:48](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4788)]
Go to that.

##### **Geohot** [[01:19:49](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4789)]
But it's not an energy.

##### **Geohot** [[01:19:50](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4790)]
This doesn't have anything to do with like, you know what?

##### **Geohot** [[01:19:53](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4793)]
This isn't some like bullshit space where like hype matters.

##### **Geohot** [[01:19:56](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4796)]
This is a real space.

##### **Chenyu** [[01:19:57](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4797)]
Just make our shit run faster than the other shit and then people will use it.

##### **Geohot** [[01:20:03](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4803)]
For?

##### **Geohot** [[01:20:03](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4803)]
Yeah.

##### **Geohot** [[01:20:04](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4804)]
Make our shit run faster.

##### **Geohot** [[01:20:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4806)]
All right.

##### **Geohot** [[01:20:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4806)]
All right.

##### **Chenyu** [[01:20:06](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4806)]
All right.

##### **Geohot** [[01:20:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4807)]
Cool.

##### **Geohot** [[01:20:07](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4807)]
Bye.

##### **Geohot** [[01:20:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4808)]
All right.

##### **Geohot** [[01:20:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4808)]
Bye.

##### **Geohot** [[01:20:08](https://www.youtube.com/watch?v=VsR6zf1bJrw&t=4808)]
Good meeting.
