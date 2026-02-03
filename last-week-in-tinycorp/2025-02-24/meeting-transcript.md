# 2025-02-24 Meeting

### Meeting Agenda

**Time:** 6am Monday San Diego time (10pm HK time)
- company update
- tiny as a torch backend, ops, as_strided, buffers
- dsp
- pow, bert, backward mem, always recompute kernel
- scheduler, become map
- am driver, usb
- tensor cores
- WebGPU (tinychat, export)
- onnx
- other bounties (retinanet, LLVM speed, LLVM for AMD, rewrite speed, rewrite add chain stuff)

### Audio

[Youtube Link](https://www.youtube.com/watch?v=Dm83mY6ONks)

### Highlights

- [5090 orders](#geohot-000011) 5090 orders are delayed until further notice.
- [Tiny as a Torch backend!!!!!!!!!!!](#geohot-000134) Progress made, but blocked by `as_strided`. Torch now recognizes TinyGrad as a backend.
- [DSP](#geohot-000612) Focus on de-vectorization. Qualcomm's DSP code is good but can be beaten.
- [POW and BERT](#chenyu-001410) Issues with `pow` causing NaNs. BERT improvements reduce memory usage by optimizing backwards.
- [Scheduler](#qazalin-002322) Reorder expand merged.
- [List of Scheduler TODOs](#geohot--qazalin--chenyu-003524) good list:D
- [AM Driver & USB](#nimlgen-003730) Working on firmware mods to improve USB GPU speed. 
- [Tensor Cores](#ignaciosica-004753) Plans to refactor `define_acc`, `assign`, `store`, and `load` to support AMX.
- [WebGPU](#hooved-004904) Enabling float16 selectively. Working on `TinyChat` PR.
- [ONNX](#chenyu-005041) Discussion on `Contrib Ops`. ONNX quantization to match ORT behavior.
- [Retinanet](#flata-005256) Fixing NaN issues in loss computation.
- [LLVM Speed](#b1tgi-005424) Investigating issue with grouped optimizations affecting FLOP estimations.
- [Rewrite Speed](#ttomsa-005749) Discussion on tree automata and equality constraints slowing down rewriting.
- [Other Bounties](#geohot-010611) More bounties planned for CIFAR and multi-GPU for torch backend.

### Transcript

##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=Dm83mY6ONks&t=0)]
Okay, let's get started.
Any company update?
5090s are delayed.

##### **Geohot** [[00:00:11](https://www.youtube.com/watch?v=Dm83mY6ONks&t=11)]
Yeah, 5090s are delayed.

##### **Chenyu** [[00:00:16](https://www.youtube.com/watch?v=Dm83mY6ONks&t=16)]
Bad.

##### **Geohot** [[00:00:17](https://www.youtube.com/watch?v=Dm83mY6ONks&t=17)]
our OEM doesn't even seem to have them yet.
You can't buy any of them on eBay yet.
And some of the other OEMs, their ones have serious problems, like all the ACES ones are getting recalled because this capacitor breaks, and then the device literally melts.

##### **Chenyu** [[00:00:40](https://www.youtube.com/watch?v=Dm83mY6ONks&t=40)]
Interesting.
OK.

##### **Geohot** [[00:00:42](https://www.youtube.com/watch?v=Dm83mY6ONks&t=42)]
So yeah, the company we're working with doesn't have any yet, probably because they have some internal testing issues.

##### **Chenyu** [[00:00:54](https://www.youtube.com/watch?v=Dm83mY6ONks&t=54)]
OK.
That's out of our control anyway.

##### **Geohot** [[00:00:59](https://www.youtube.com/watch?v=Dm83mY6ONks&t=59)]
Yeah.
No, like, we were going to get them, they gave us a date, and then they're like, nope, psych.
And I don't think they rugged us to give them to someone else.
I think there was a problem with them.
So, well, I'd rather they be late than broken.

##### **Chenyu** [[00:01:20](https://www.youtube.com/watch?v=Dm83mY6ONks&t=80)]
Yeah, of course.
Cool.
We have a pretty big item.
You want to talk about Tiny as a Torch backend?

##### **Geohot** [[00:01:34](https://www.youtube.com/watch?v=Dm83mY6ONks&t=94)]
Sure.
But I really do have to hand this off, because I have to get back to the DSP.
Yeah, yeah.
I got a lot done this week.
I'm happy that I
laid down the groundwork for it.
I'm happy with where it is.
Backend.py, not backend2.py.
So it turns out that Torch has this layer right below it called aten that it uses.
And aten is very similar to tensor.py.
So it's pretty easy to just point Torch to all the tinygrad methods and then register a new device in Torch called tiny.
And then it's like..
it wraps TinyGrad.
So now Torch code runs, but just right below the surface, it's all of TinyGrad.
It's Torch's gradient API.
But yeah, everything else is TinyGrad.
And yeah, I think there's good progress there.
And this is going to unlock a lot of testing too, because we'll be able to use all of Torch's tests to test TinyGrad.
Like this will just be a backend in the same way like MPS and CUDA are Torch backends.
Tiny will be a Torch backend.

##### **Chenyu** [[00:02:46](https://www.youtube.com/watch?v=Dm83mY6ONks&t=166)]
Did this start here because Sumit replied to your tweet or something?

##### **Geohot** [[00:02:50](https://www.youtube.com/watch?v=Dm83mY6ONks&t=170)]
Yeah, Sumit replied.
Another one of the Torch guys replied on a different thread.
And then I started thinking about it a little.
And I'm like, wait, this is actually a really good idea.
And this will allow Torch to get on every device Tiny gets on.
It's just a great way to kind of, we don't want to compete with PyTorch.
We want to become a part of PyTorch.
That's winning.

##### **Chenyu** [[00:03:16](https://www.youtube.com/watch?v=Dm83mY6ONks&t=196)]
Yeah, I think one thing I was reading the changes, it's a good validation of TinyGrad.
It's quite mature or good that we cover a lot of core concepts that needs to make this work.

##### **Geohot** [[00:03:33](https://www.youtube.com/watch?v=Dm83mY6ONks&t=213)]
Yeah.
We haven't gotten to the edge cases yet.
So as_strided is probably the trickiest one, because it's unclear even what it means in TinyGrad.
What if you call as_strided twice on something?

##### **Chenyu** [[00:03:53](https://www.youtube.com/watch?v=Dm83mY6ONks&t=233)]
I thought you just get your movement ups and stack those.

##### **Geohot** [[00:03:57](https://www.youtube.com/watch?v=Dm83mY6ONks&t=237)]
No, definitely not.
That's not what Torch does, right?
If I have a tensor and I call as_strided on it, and then I call as_strided again, they don't stack.
At least..

##### **Chenyu** [[00:04:13](https://www.youtube.com/watch?v=Dm83mY6ONks&t=253)]
I mean stack as in you know what the move needs to be done and you can figure out the underlying algebra of it.

##### **Geohot** [[00:04:22](https://www.youtube.com/watch?v=Dm83mY6ONks&t=262)]
No, no, no.
But I mean like, okay, so if I have something that has like, it's a 10 by 10 tensor that has strides 10, 1.
And then I do as_strided 1, 10.
And then I do as_strided 1, 10 again.
That doesn't permute it back, I don't think.
I think that's still the same permuted tensor.

##### **Chenyu** [[00:04:42](https://www.youtube.com/watch?v=Dm83mY6ONks&t=282)]
Oh, I see.
OK.

##### **Geohot** [[00:04:45](https://www.youtube.com/watch?v=Dm83mY6ONks&t=285)]
I'm not sure.
But yeah, I need to work on the DSP stuff.
I have to hand this off, and I can't spend a ton more time on it, at least for now.
But yeah, how do you feel about taking it over?

##### **Chenyu** [[00:05:01](https://www.youtube.com/watch?v=Dm83mY6ONks&t=301)]
Oh this one?

##### **Geohot** [[00:05:03](https://www.youtube.com/watch?v=Dm83mY6ONks&t=303)]
Just the torch back end in general.
It's similar to ONNX.

##### **Chenyu** [[00:05:08](https://www.youtube.com/watch?v=Dm83mY6ONks&t=308)]
Yeah, sure.
I don't know what that means, but sure.

##### **Geohot** [[00:05:14](https://www.youtube.com/watch?v=Dm83mY6ONks&t=314)]
just responding to the bounties, putting up more bounties.

##### **Chenyu** [[00:05:19](https://www.youtube.com/watch?v=Dm83mY6ONks&t=319)]
Yeah, I can do code-review and manage this stuff.
And I think pretty much everything is blocked by as_strided.
So if people are interested in trying, I will point to the old implementation so people can take a look.
I'm pretty sure if we write it, we will just test it through torch's test.
And if we pass those, we are probably correct.

##### **Geohot** [[00:05:46](https://www.youtube.com/watch?v=Dm83mY6ONks&t=346)]
Yeah, I agree.
It's also, it's weird.
The as_strided call is not being called with what I would think of as strides.
So I'm using this, yeah.

##### **Chenyu** [[00:05:57](https://www.youtube.com/watch?v=Dm83mY6ONks&t=357)]
There's also empty strided.
I saw you just implement it as empty taking a shape, but I don't think that's correct.

##### **Geohot** [[00:06:04](https://www.youtube.com/watch?v=Dm83mY6ONks&t=364)]
I don't think that's correct either.
Yeah. So this is.. 

##### **Chenyu** [[00:06:06](https://www.youtube.com/watch?v=Dm83mY6ONks&t=366)]
You can repeat, right?
Then you are allocating much bigger memory and things like that.

##### **Geohot** [[00:06:12](https://www.youtube.com/watch?v=Dm83mY6ONks&t=372)]
Yes.
So I can either do this this week or the DSP.
And I really think.. 

##### **Chenyu** [[00:06:17](https://www.youtube.com/watch?v=Dm83mY6ONks&t=377)]
Please do DSP that has a deadline.

##### **Geohot** [[00:06:23](https://www.youtube.com/watch?v=Dm83mY6ONks&t=383)]
The DSP has a deadline.
And today what I'm realizing is the real thing.
80% of doing the DSP is getting de-vectorized, to be correct.
So it's not just the DSP, it's migrating Devectorize to the other type of Devectorize.
The problem with the old Devectorize type is it's just clearly not designed for things that have 128 elements.
Like it will work, but it's so slow because it's creating 128.

##### **Chenyu** [[00:06:52](https://www.youtube.com/watch?v=Dm83mY6ONks&t=412)]
Yeah, because you are creating a combination of everything.

##### **Geohot** [[00:06:56](https://www.youtube.com/watch?v=Dm83mY6ONks&t=416)]
Yeah, yeah, exactly.
So you just shouldn't be doing that.
And the old thing was a hack.
So I have to get the new one to work and work correctly.
And, like, now I'm dealing with all sorts of stuff where it's like, so I added some stuff to add in an ignore UOp, which can push through the stores, which can, it fixes all the const things.
So I have all the const things fixed.
But now, in order to really make the conv fast, you have to upcast it on both the horizontal and the vertical.
And then when you upcast it on the vertical, you get holes in the store.

##### **Chenyu** [[00:07:32](https://www.youtube.com/watch?v=Dm83mY6ONks&t=452)]
Uh-huh, uh-huh.

##### **Geohot** [[00:07:34](https://www.youtube.com/watch?v=Dm83mY6ONks&t=454)]
Well, it's not even, like, I don't even think they're really holes.
I think it's contiguous, but, like, the problem is some of the stores are false, and that's not really supported correctly.
Like, yeah, yeah, yeah, yeah.
If you have, like, if you have a store to, like, 0, 1, 2, 3, 4, 4, and 5, right, like, one of those 4s has to be false.
You've got to support that.
It's not that it's hard, but.
like the current stuff just doesn't work with this, so yeah the first move is to like the other de-vectorized and then I think that's it I think with those two things we'll get the DSP down to 50 milliseconds and then there's another 2x to actually using the intrinsic methods and then there's another 2x to using the two cores and that's the whole thing
Qualcomm's code is actually extremely good, unfortunately.

##### **Chenyu** [[00:08:44](https://www.youtube.com/watch?v=Dm83mY6ONks&t=524)]
No, I leave that to you.

##### **Geohot** [[00:08:47](https://www.youtube.com/watch?v=Dm83mY6ONks&t=527)]
It's clear they put a lot more effort into the DSP than the GPU.
Their DSP code is actually good.
We can beat it, but it's not easy.
It's not like I can leave something on the table.
I have to do everything.

##### **Chenyu** [[00:09:04](https://www.youtube.com/watch?v=Dm83mY6ONks&t=544)]
Yes.
OK.
Yeah, I think for Torch back-end, we just, the infra is there.
The testing is there.
It's fairly clear.
If you get something right, you will see the failure number goes down.
So I think that's good for Bounty, similar to ONNX.

##### **Geohot** [[00:09:30](https://www.youtube.com/watch?v=Dm83mY6ONks&t=570)]
Yeah, if you could just manage the people.
Look, everyone here who wants to contribute to the,
the Torch backend.
Let's get on it.
Let's get some good bounties up for it.

##### **Chenyu** [[00:09:42](https://www.youtube.com/watch?v=Dm83mY6ONks&t=582)]
Yeah, that's fine.
Do you want to comment on something?
I saw a tweet that you were trying this for some speed thingy.

##### **Geohot** [[00:09:52](https://www.youtube.com/watch?v=Dm83mY6ONks&t=592)]
Oh, yeah.
I tried GPU MODE.
They have a kernel competition.
to do who can get the fastest kernels.
So I just took one of them, wrote a tinygrad implementation, and hey, we beat everybody.
We actually go back to not beating everybody if we use the from blob stuff, because the from blob stuff adds a couple hundred microseconds of Python time.
So then we lose to Triton again.
But it's, yeah, at least the code is very clean now with the from blob for CUDA.
So yeah, we can try writing the other ones.
And that's just like with BEAM 2.
It was very simple to write.
So yeah, we have the fastest kernel for gray scale.

##### **Chenyu** [[00:10:41](https://www.youtube.com/watch?v=Dm83mY6ONks&t=641)]
Which kernel is that?

##### **Geohot** [[00:10:43](https://www.youtube.com/watch?v=Dm83mY6ONks&t=643)]
So I don't know why it's faster than Triton.
It should be like the same speed as Triton.
But it's faster than the Torch one.
It's grayscale.
So it's just like, take an RGB image, multiply RGB by consts, and then.

##### **Chenyu** [[00:10:59](https://www.youtube.com/watch?v=Dm83mY6ONks&t=659)]
So just element-wise.

##### **Geohot** [[00:11:01](https://www.youtube.com/watch?v=Dm83mY6ONks&t=661)]
Element-wise, yeah.
Element-wise multiplication fused with just add them all together.

##### **Chenyu** [[00:11:07](https://www.youtube.com/watch?v=Dm83mY6ONks&t=667)]
Weird.

##### **Geohot** [[00:11:09](https://www.youtube.com/watch?v=Dm83mY6ONks&t=669)]
I want to see why Torch is slow.
Torch didn't make them consts.

##### **Chenyu** [[00:11:15](https://www.youtube.com/watch?v=Dm83mY6ONks&t=675)]
Are you sure?
In the aten, there's definitely things with const and things with tensor.

##### **Geohot** [[00:11:24](https://www.youtube.com/watch?v=Dm83mY6ONks&t=684)]
Yeah, well, no.
But they can't, like, Torch doesn't support anything that looks like multi-const.
So it's not, you have to multiply, like, the three things by three different values.
So Torch can do this in two ways.
Torch can either do, like, a multiply and then a sum, which is a huge waste of memory.
Or Torch is doing an extra complete write out to memory.
And that's why it's way slower.
no matter which way you do it in Torch.

##### **Chenyu** [[00:11:58](https://www.youtube.com/watch?v=Dm83mY6ONks&t=718)]
Sounds good.
Good progress, pretty active channel.
I also find Torch people more reasonable to work with compared to you know who.

##### **Geohot** [[00:12:11](https://www.youtube.com/watch?v=Dm83mY6ONks&t=731)]
But yeah, the Torch people are great.
We're super happy to have them here.
Yeah, yeah.
Who landed?
Someone landed a..
One of the Torch guys landed a PR today.
It was a great PR.
All Ben D landed a simplified C++ with PR.
And it was something I was struggling with for just about 15 minutes trying to do that, and then just ended up writing this stupid code from ChatGPT.
And he's like, yeah, you don't need any of it.
So that's great.

##### **Chenyu** [[00:12:46](https://www.youtube.com/watch?v=Dm83mY6ONks&t=766)]
Great.

##### **Geohot** [[00:12:48](https://www.youtube.com/watch?v=Dm83mY6ONks&t=768)]
No, I mean, someday I'd like to get this upstreamed into Torch.
Even if it's like six months from now, but yeah.

##### **Chenyu** [[00:12:58](https://www.youtube.com/watch?v=Dm83mY6ONks&t=778)]
No, sounds good.
OK, moving on to my part.
For POW, a mistake.
Also, people are getting NaN from very simple stuff.
So I reverted part of that back.
And I think in the implementation in Transcendental, these like goals also commented saying that in addition to zero we have problems, info also have problems, and I imagine an AM will have problems, the usual suspect in Transcendental.
But I need that.
I also fix.
But I think for now, the usual use case, I think the most common case, if you do a power to integer, it's reverted to the back old behavior.
So that should be correct.
And moving on to BERT.
So I so-causally merge that reorder expand thing.
I don't think that's faster.
Yeah, that's just merged.

##### **Chenyu** [[00:14:10](https://www.youtube.com/watch?v=Dm83mY6ONks&t=850)]
Oh, just merged.
OK, I was going to say, yeah.
Awesome.
That's a great victory, because if we can do that, we can do a lot more things that look like that.
Oh, that's going to make.
That's going to get us a 20% speed up on BERT with a bunch more of those rules.

##### **Chenyu** [[00:14:41](https://www.youtube.com/watch?v=Dm83mY6ONks&t=881)]
So I do a late bunch of parts in BERT model and find out that Softmax was using a quarter of total memory.
And I think there are two things here.
So one is we were storing all the Softmax stuff in float.
But if we are doing float 16 training, it's possible to do lows in half and in the backward use the half version of the output.
So I have a PR for that.
I will merge it maybe today.
And that allows us to increase the batch size from 66 to 78.
And that's 10% faster.
I did a bunch of training, so now it's pretty stable.
I think our time is around 4.5 hours now, improving from our previous submission.
So I think things like this, I don't think ReLU has this problem, but things like softmax or sigmoid,
there's this concept of you don't really need every output of gradient to figure out your backward.
For example, the simplest case is for sigmoid.
You only need to know sigmoid output to do the backward.
But for now, because we break it down into smaller parts, some of it will store some intermediate version of sigmoid.

##### **Geohot** [[00:16:26](https://www.youtube.com/watch?v=Dm83mY6ONks&t=986)]
So in order to fix that, there's two ways to fix it.
One way to fix it is to like, so it's all about how many long edges there are in the graph, like long edges going from the beginning of the graph to the end of the graph.
So there's two basic ways to remove.

##### **Chenyu** [[00:16:46](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1006)]
Yeah, that's the part that also points to the buffers we need to store to prepare for backend.

##### **Geohot** [[00:16:56](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1016)]
Yeah, so I don't know exactly what this is going to look like generically.
And I don't know if we want to try to do anything to detect those long edges.

##### **Chenyu** [[00:17:05](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1025)]
You go first.
Well, there's two ways to do it, right?

##### **Geohot** [[00:17:13](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1033)]
So you can either change the math to not have the long edges with rewrite rules, or you can redo the math.
You can somehow tell the kernel at the end, hey, don't store a and a plus 1.
Just recompute a plus 1 every time you need it.

##### **Chenyu** [[00:17:29](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1049)]
Yes.
So that's what I mean for always recompute kernel.
Basically, there are some kernels we are happy to always recompute it and never realize it as a real buffer and reuse that buffer.
So one example I can give you is dropout.
Triton also mentioned this.
Because dropout, the random kernel is just element-wise.
So you are pretty much always happy to recompute that and use the dropout, that mask in the backward.
Similar things for softmax is probably possible, but I don't quite understand how to do this.
Conceptually, it's the same thing as what you said.
You tag it, or you say just demo-materialize this.

##### **Geohot** [[00:18:29](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1109)]
Yeah.
You have something that you always want to recompute.
That's pretty easy.
That's pretty easy to make a rule.
We could always say, why would you ever store a plus 1?

##### **Chenyu** [[00:18:41](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1121)]
Mm-hmm.
Yeah, so I think element-wise, maybe to start with, then we can see if that worked for dropout, then think about more.
So I think for one great contribution for Flash attention seems to be they figure out the minimal information you need for backwards, and it does that pretty well.
So you store very little information.
I think for softmax, they only need the output of exp2.
So things like that.

##### **Geohot** [[00:19:18](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1158)]
Well, yeah.
So there is a whole fancier thing, too.
So let's say for some reason you've already stored a plus 1.
And you have to store a plus 1.
A plus 1 is the one you have to store on the forward pass.
So there's this concept in the backward pass of, OK, well, I need a in the backward pass.
But you've already stored a plus 1.
So how do you invert it?
There should be a way to invert the whole thing and say, oh, actually, just compute it from this one by subtracting one.
And that's the next level of this.

##### **Chenyu** [[00:19:52](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1192)]
OK, let's get in too ahead of ourselves.

##### **Geohot** [[00:19:56](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1196)]
Well, I mean, that's.. 

##### **Chenyu** [[00:19:56](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1196)]
I don't quite see the reason why you want to store A plus 1 if you already have A. 

##### **Geohot** [[00:20:05](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1205)]
Because you need it for the forward pass.

##### **Chenyu** [[00:20:09](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1209)]
Or maybe you need it directly for the output.

##### **Geohot** [[00:20:13](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1213)]
Or, yeah, or you need it directly for the output.
But, like, let's say you need it for the forward pass, right?
Let's say the thing after A plus 1 is a big expand.
Like, a really big expand.
Like, a 100x expand.
So you're going to store A plus 1.
But the backward pass needs A. The backward pass needs A unexpanded.
You're better off subtracting 1 from the A plus 1.
Yeah, these all come down to whether you want to detect long edges.
The inverse thing is not hard to write.
It's easy to write.
It's just hard to know when to trigger it.

##### **Chenyu** [[00:20:53](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1253)]
Yeah, so I'll probably see if I can do that for dropout.
So dropout, if we can save those.
I guess the dropout is the size of intermediates from attention.
So if we can save that, that's another 10% memory save.
So my current learning is our memory
scheduling is pretty optimal, and our memory use really is all the intermediates that we need for backward.

##### **Geohot** [[00:21:25](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1285)]
Oh, yeah.
Our scheduling is phenomenal, but we don't really need all those intermediates for backwards.
The thing called memory scheduler is perfect, pretty much.
There's not going to be much improvements to be made there.
But where the improvements are to be made is reducing the number of long edges.

##### **Chenyu** [[00:21:44](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1304)]
Uh, yes.
So do you have a suggestion for like tagging this in debug information or VIZ?

##### **Geohot** [[00:21:53](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1313)]
Yeah, I guess we could write like, like there's a question where..
Yeah.
Yeah.
Like, do we want to explicitly track this concept of a long edge?
And I think maybe for now we do.
Since gradient is all below the tinygrad API line.
So since we know things are backward in the metadata, we should have this idea of a long edge, which is something that connects from a forward to a backward.
And then we can have a bunch of rules whenever something's a long edge, like do the inverse or something.

##### **Chenyu** [[00:22:32](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1352)]
I don't know if we want to do logic depends on that.
I was more thinking about surfacing as a debug information.
So you don't need to.
like me do a plate of model and realize stuff like this.

##### **Geohot** [[00:22:46](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1366)]
That sounds like a better place to start, yeah.

##### **Chenyu** [[00:22:49](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1369)]
OK, great.

##### **Geohot** [[00:22:50](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1370)]
We could color it in Viz or something.

##### **Chenyu** [[00:22:54](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1374)]
OK.
Anyway, making progress.
I think four hours is definitely a more reasonable time to iterate than six hours.
I'm quite happy about that.
I also need to test this AMD and AM.
I don't know if it's good now.
I will do that later.
OK.
Let's move on to scheduler.

##### **Qazalin** [[00:23:22](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1402)]
So my big thing was reorder expand.
I just merged that.
It turns out a lot of these stuff are just generic things, the generic refactors.
I removed a bunch of lines, like maybe around 30 lines from the scheduler last week.
Just simplifying things, cleaning things up.
We're in a good spot to start really doing the speed-up fusions.
Chenyu saw me push right before the meeting.
I am working on one kernel softmax.
Just first understanding if we can swizzle this correctly.
Right now, the swizzling still needs work.
So this week, I'm just going to work on putting those reduces in one kernel, seeing if we can code-gen it, and then moving on to actually writing the rule that will detect that and not realize the kernels in the intermediate buffers.
That's going to be quick.

##### **Geohot** [[00:24:27](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1467)]
So are we ready for this?
Um, I think that single kernel softmax still has like, I'm curious why we can't do it.
But I looked into it a little bit.
And it involves a lot of fancy stuff with local memory.
I think we might have lower hanging fruit still with the like, realize expand.

##### **Chenyu** [[00:25:05](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1505)]
I think we realize expand far more often than we have to.

##### **Geohot** [[00:25:15](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1515)]
So I might suggest looking at this before trying to do what I think the
hard part of single kernel softmax is.
Single kernel softmax is going to basically require you to compute the entire max in locals.
Does that agree with what you've seen?

##### **Qazalin** [[00:25:44](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1544)]
At this point, I haven't even been able to make the shape trackers work correctly, like merge the views such that there is some valid AST.
I don't know.

##### **Geohot** [[00:25:59](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1559)]
we should focus, before we focus on that, on still trying to make the scheduler more.. Right now, if I wanted to figure out which expands are being realized, how could I apply a rule to that?

##### **Qazalin** [[00:26:22](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1582)]
There's still part of the scheduler I haven't migrated, which is the
rule that realizes the expands.
That's always going to trigger.
I think what we have to end up doing is something like reorder expand that I just merged, which is pushing that expand over to the op that we want before that realization rule runs.

##### **Geohot** [[00:26:47](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1607)]
Yeah.
Good work on this.

##### **Qazalin** [[00:26:51](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1611)]
OK.
I was thinking about adding cast before view back, because now we can.
So maybe I'll start seeing how that goes.

##### **Geohot** [[00:27:03](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1623)]
I like this direction.
I think we're still maybe a month away from single kernel softmax.
And then before that, I like to break the scheduler into some.
Oh, the other thing, too, is do you have the kernels going back?
Do you have becomes map working?

##### **Qazalin** [[00:27:30](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1650)]
I had to make a compromise and add the views back.
We can't reverse.. 

##### **Geohot** [[00:27:35](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1655)]
Well, the views are OK.
But what I'm saying is by becomes map.
So like right now, we have the BFS still in the scheduler.
Like on line 435, there is view kernel graph.
And then afterward, there's the BFS.
Let me actually make sure I'm on the latest.
Can we make the entire operation of scheduling a becomes map?

##### **Qazalin** [[00:28:12](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1692)]
Map tensors to kernel ops?

##### **Geohot** [[00:28:16](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1696)]
Yeah.
So the tensors, after a tensor is scheduled, it will become a kernel op.
Does this make sense?

##### **Qazalin** [[00:28:32](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1712)]
Yeah, it makes sense.
I think if you read the becomes map, it's actually what it does.
Tensors can become three things.
They can become an assign, they can become an existing realized buffer, or they can become a const.

##### **Geohot** [[00:28:50](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1730)]
Well, no.
What I'm saying is, so right now, createScheduleWithVars is still returning a list of schedule items.

##### **Qazalin** [[00:28:59](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1739)]
I'm going to return it.

##### **Geohot** [[00:29:02](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1742)]
I want to return Yes, only a becomes map, then I want the I want to basically move the schedule item creation to realize.
So what this unlocks is the creation of a tensor graph that is scheduled.
Right now, um, when we
So this has to do with how I want to refactor the JIT.
I want to separate scheduling even further from realization.
So right now we have the scheduler outputting.
The scheduler and the linearizer are the same thing right now.
Like the schedulizer and the schedule linearizer are the same thing.
The schedule linearizer should be factored out of the scheduler.
So we could do things like with the JIT, we could schedule everything in the JIT and then linearize it all as one thing.
And that's the exit of the JIT, right?
So let's say in the JIT, I call schedule or realize multiple times.
I would like that not to become a list and it can become a list later.

##### **Qazalin** [[00:30:25](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1825)]
I see.
Does the assign fixup also end up in the JIT?

##### **Geohot** [[00:30:36](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1836)]
No.
No, the assign fixup where we add the extra edges?
I believe adding the extra edges belongs in the scheduler.
Yes, yeah, so all the stuff, basically like create schedule with vars should stop at line 435 and returning becomes map.
Great.
I think this is lower priority, though, than cast before view.
I think cast before view and everything that looks like messing with those expands is the highest priority.
And I think that is going to get us gains on BERT.
And gains across the board.
Oh, and is multi-kernel back?

##### **Qazalin** [[00:31:39](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1899)]
No, multi-output isn't back.

##### **Geohot** [[00:31:42](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1902)]
Multi-output isn't back.
And then how about, do the views still exist in the VIZ graph?
In the kernel graph.

##### **Qazalin** [[00:31:50](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1910)]
I'm struggling with sub-buffer.
Buffer view is just ugly.
I don't know.
What is the buffer view?
Is it a buffer view view buffer?
The only reason it exists is because of the setitem.

##### **Geohot** [[00:32:11](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1931)]
Wait, pardon me?
The only reason it exists is for the what?

##### **Qazalin** [[00:32:13](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1933)]
For setitem.
So setitem does a shrink on a buffer.

##### **Geohot** [[00:32:20](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1940)]
OK.

##### **Qazalin** [[00:32:24](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1944)]
The views should match, right, between the sources of the assign.
So your suggestion was that the assign source 0 actually doesn't become a buffer view.
It becomes a sub-buffer.

##### **Geohot** [[00:32:40](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1960)]
It becomes a sub-buffer.
But are you saying sometimes they're non-contiguous?
Oh, I like that you changed the schedule 1.
That looks nice.

##### **Qazalin** [[00:32:48](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1968)]
Yeah.
That's the only reason it exists.
I don't know what sub-buffer looks like.
Is it a buffer view op that has a src zero buffer and then an arg ShapeTracker?

##### **Geohot** [[00:33:11](https://www.youtube.com/watch?v=Dm83mY6ONks&t=1991)]
Buffer view is just a buffer with an offset.
So it's the same as when you offset a buffer.
You can also change the size.
So you know the function offset in buffer?

##### **Qazalin** [[00:33:35](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2015)]
Oh, yeah, yeah, yeah.

##### **Geohot** [[00:33:36](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2016)]
It's that, basically.

##### **Qazalin** [[00:33:39](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2019)]
So does buffer view basically have an arc that's a tuple?
That's exactly what the device buffer takes?

##### **Geohot** [[00:33:46](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2026)]
Yes.
It is actually exactly the, it's called the view function on buffer.
So that, it includes a size, a Dtype, and an offset.
So the, actually, yeah, it'll just include a tuple of the size and the offset.
And the Dtype is the Dtype of the thing.

##### **Qazalin** [[00:34:06](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2046)]
Okay.
I have the confirmation.
I'll make it work.
That's the last thing I have to do.
Cool.

##### **Geohot** [[00:34:12](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2052)]
Yeah, but most of them won't need views.
I think they'll only need a buffer view if something shrinks.

##### **Qazalin** [[00:34:17](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2057)]
Yeah, only if there's a setitem.

##### **Geohot** [[00:34:21](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2061)]
Only if there's a setitem.

##### **Qazalin** [[00:34:23](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2063)]
And then all the shapes, all the extra shapes are local.
Like if you have a kernel that's outputting a 32 by 32,
the ShapeTracker of that one becomes something in the local kernel AST.
It's like the kernel graph will only know of sizes.

##### **Geohot** [[00:34:42](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2082)]
The kernel graph should only know of sizes, right?
Because the kernel graph can only handle one dimensional.
That's how the memory system of these things work.
If I put it like, if I pass in a, think about it, if I pass in a pointer to a GPU kernel, that pointer has a start and a size.
And those are the two things on that pointer.
That pointer doesn't know anything about strides or anything like that.
It's a one-dimensional memory system.

##### **Geohot & Qazalin & Chenyu** [[00:35:24](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2124)]
Cool, but yeah, I think that's a good list.
Buffer view.
Becomes map.
Multi-output.
Cast before view.
What about multi?
Multi-output.
Oh, multi-output.
Yes, multi-output.
Yes.

##### **Qazalin** [[00:35:42](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2142)]
It's annoying
I'll try to bring it back.
Is it high priority?
I don't think it brings so much gains at this point.

##### **Geohot** [[00:35:51](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2151)]
No, but we need to bring it back because it needs to be supported.
What multi-output
is multi-output changes the semantics of these graphs.
It changes the spec of the graphs.

##### **Qazalin** [[00:36:06](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2166)]
One kernel can point to multiple assigns?

##### **Geohot** [[00:36:09](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2169)]
Yes.
One kernel can point to multiple assigns, yes.

##### **Qazalin** [[00:36:14](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2174)]
The reason why it's annoying is because the realization logic isn't actually integrated into the kernel creation.
There's a separate stage that just adds Tensor UOps to a dictionary.
Multi-output will require me to refactor that whole thing.
It's going to take me a couple of days.

##### **Geohot** [[00:36:36](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2196)]
Let's do it correctly.
This is why I'm interested in multi-output.
Multi-output forces correctness in a certain way.
Because if whatever we've designed can't support multi-output, we're missing something.

##### **Qazalin** [[00:36:49](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2209)]
Yeah, the design can support it.
It's just that the logic for deciding which tensor to realize is still custom.
It shouldn't be.

##### **Geohot** [[00:36:58](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2218)]
You have to realize them both.
But cool, yeah, yeah.
All these things definitely before multi-output softmaxes, single kernel softmaxes is a long way away.
But we're getting there.
We're making progress.
This is it.

##### **Chenyu** [[00:37:15](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2235)]
Great.
That's a good list of things to do.
Let's move on to driver.

##### **Nimlgen** [[00:37:30](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2250)]
Yeah, so for the USB GPU stuff, so I started to work on firmware mods.
So yeah, things aren't speed set to low.
It's just 2 kilobytes a second.
After the latest optimizations, we need to load about 60 megabytes.
Yeah, it's loaded right now.
So the current plan is actually to move the whole logic of accessing TLP to a different layer.
And that should be faster.

##### **Geohot** [[00:38:11](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2291)]
Do we have to do this?
Is there going to be any way around this?

##### **Nimlgen** [[00:38:20](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2300)]
So, no, actually to send TLP, the only way we can send TLP is access this register, like memory map tag or all these things.

##### **Geohot** [[00:38:36](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2316)]
There's not like another pathway in the firmware that accesses the TLP?

##### **Nimlgen** [[00:38:41](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2321)]
Yeah, that's for sure.
For TLP, yeah.

##### **Geohot** [[00:38:46](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2326)]
By the way, tiny4 is down right now.
Do you know why?

##### **Nimlgen** [[00:38:49](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2329)]
Yeah, I'm just rebooting it.

##### **Geohot** [[00:38:51](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2331)]
Oh, you're rebooting it.
OK, but you saw everything's up on Tiny4 now.
It's moved.
You should be able to reboot it all you want.

##### **Nimlgen** [[00:38:57](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2337)]
Yeah, yeah, yeah.
It works.
It's great.
So yeah, the plan is to move the logic.
At least we can get decent speed.
And after we get the GMA, it's OK.
Yeah.

##### **Geohot** [[00:39:13](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2353)]
you're sure you've checked all the methods and there isn't some other faster method to access multiple, to send multiple TLPs?

##### **Nimlgen** [[00:39:24](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2364)]
Yeah, yeah, yeah.
I think all this custom, like, we have several custom comments, which is, like, not perfect, which we use to access some registers and external memory.
So, yeah.
There's no methods to access it in a custom way.

##### **Geohot** [[00:39:45](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2385)]
Yeah.
Okay.
Then it requires custom firmware.
Does the firmware.. Is the firmware downloaded every time to the chip, or the firmware lives in some flash on the chip?

##### **Nimlgen** [[00:40:04](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2404)]
So, actually, they have, like, the third version, they have some
Yes, so he has some code to upload this firmware.
I'm not sure.
So I'm sure maybe back in my firmware or something, I don't know.
But yes, the patching is simple method.
I don't see any changes right now.

##### **Geohot** [[00:40:35](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2435)]
Whenever we get to custom firmware, we have to ask some questions.
It's like, can we brick it?
Is it still compatible?

##### **Nimlgen** [[00:40:41](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2441)]
Yeah, just try to do everything to not brick it.

##### **Geohot** [[00:40:49](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2449)]
Well, no, I know.
We're going to brick it.
Now, is it brickable?

##### **Nimlgen** [[00:40:57](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2457)]
I think in theory, yes.
Of course, if we just remove the flash comment on it,
from the firmware and upload the new firmware without comment yet.
I think it's difficult to do that.
I don't know.
Maybe there's some storage, some resource storage to fortify it.

##### **Geohot** [[00:41:15](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2475)]
Yeah, or maybe there's some mode you can boot it in.
There's some bootloader mode that's.. 

##### **Nimlgen** [[00:41:26](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2486)]
Yeah, I haven't found this.
And I think that there's nothing in the docs like the original.

##### **Geohot** [[00:41:35](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2495)]
It's good to try to find those things beforehand while you still have the ability to dump RAM on the chip and stuff.
I mean, it would kind of surprise me.
OK, maybe there's some pin you short which puts it in DFU mode, because there's some way the firmware gets loaded originally.
We have some docs for that chip, too.
I think I sent them to you.
They're not that useful.
I have a datasheet.
It tells me all the pins.
Did I send you the datasheet?

##### **Nimlgen** [[00:42:27](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2547)]
No, but I think I have something.

##### **Geohot** [[00:42:33](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2553)]
If I didn't send you the data sheet, it's not a public data sheet, but it is a data sheet, and I will send it to you.
Yeah, I mean, we should look.
Custom firmware is scary for all the reasons that like, OK, I'm not worried about it because it costs money or anything.
I'm worried about actually deploying this thing to people.
And it would be a lot easier if we could use the firmware that was already on there, right?
Because now it's like, oh, I unplugged my thing and it broke it.
And now I'm angry and I'm posting a tinygrad issue about it.
So yeah, if you break a few of these, I don't care.
But if like there's any way we can find a way to make them unbreakable, it's worth investigating.
How does, wait.
How does this work if you're using it?
So are you talking just about the 23 or the 24 chip?

##### **Nimlgen** [[00:43:32](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2612)]
I think they're pretty close to each other.
Yeah.
I'm doing this on the 23.

##### **Geohot** [[00:43:41](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2621)]
You're doing it on the 23.
So the 24 can actually support GPUs.
The 24 is designed for GPUs.
They're just only supposed to work over Thunderbolt.

##### **Nimlgen** [[00:44:05](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2645)]
So, yeah.
Yeah, actually, I think I've just looked mostly into the, like, the way how,..

##### **Geohot** [[00:44:47](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2687)]
This one supports USB 4, though, which does work for GPUs.
They're 24.
So I wonder if there's another path.
I know very little about the USB 4 spec.
I know it's a lot more like Thunderbolt, where it maps an entire memory.
So maybe you're just actually mapping it or something.

##### **Chenyu** [[00:45:30](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2730)]
Is it cool that we put this in the channel and move on?

##### **Geohot & Nimlgen** [[00:45:36](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2736)]
Yeah.
So yeah, OK.
I'll be able to check the 24.
So yeah, and for metal, yeah.
Oh yeah, for metal, yeah.
Yeah, I mean, for metal, I can finish this.
I'll take a look.
Cool.
Yeah, it looks like it's on a private heap.
I'm not sure why it doesn't work.
Yeah, it's strange.
I mean, it's just, yeah, we just see zeros when we read from these buffers.
And when we write to these buffers, I don't know, a different location or something.

##### **Geohot** [[00:46:15](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2775)]
Yeah.
Maybe I have to specify that.
I think there's some metal method to use a private heap.
We could also put the USB project on hold for a bit and move to making NV work with the torch kernels.

##### **Nimlgen** [[00:46:44](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2804)]
OK.

##### **Geohot** [[00:46:47](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2807)]
Maybe that's a better project for now.
We'll put USB on hold until we find, like, because the minute we start doing firmware mods, it's just, it's a rabbit hole.
And I feel like it's, like, it's not going to be the good solution we want to ship anyway.

##### **Nimlgen** [[00:47:06](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2826)]
Oh, yeah, okay.
I mean, it's okay.
I'll double-check the firmware again for the 24.

##### **Geohot** [[00:47:13](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2833)]
Yeah, and if there's nothing obvious, let's put it on hold for a week or two, get the NV Torch thing working.
And then I'm hoping with that NV Torch thing, we can get people starting to look into kernel performance.
Like, why does Torch have faster comms than us and stuff?

##### **Chenyu** [[00:47:36](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2856)]
OK.

##### **Chenyu** [[00:47:44](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2864)]
Let's try to be faster for the rest of items.
Let's move on to Tensorcores.

##### **Ignaciosica** [[00:47:53](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2873)]
Hi.
Hello.
About last week, not much to share.
I couldn't work much.
This one, I'm going to start with the refactor on define_acc and the assign to store and load, and then follow from there.

##### **Chenyu** [[00:48:12](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2892)]
This is for the AMX?

##### **Ignaciosica** [[00:48:17](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2897)]
Yes.
It's not strictly related, but I think it's a good way to start getting into what I need to do in order for the AMX.

##### **Chenyu** [[00:48:31](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2911)]
That sounds good.
OK, so WebGPU Wpmed said, only enable float 16 if any of the kernel has float 16.
You can choose the backend for dawn and putting together a PR for blah.
OK.
Hooved, you have anything you want to share?

##### **Hooved** [[00:49:04](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2944)]
Not that much.
I've been getting the TinyChat PR ready for merge, which is mainly involving a refactor of my compile and export model stuff into export model.py.
So it's starting to overlap with the other bounty, but not quite because I'm not moving anything into main TinyGrad yet.

##### **Chenyu** [[00:49:30](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2970)]
OK, let's see.
I don't know.
George, what's your comment on that?
Is there a way that we don't touch this other bounty and find a way to finish the TinyChat one first?

##### **Geohot** [[00:49:43](https://www.youtube.com/watch?v=Dm83mY6ONks&t=2983)]
I mean, yeah.
Let's get TinyChat merged out of tree and then think about how to move it into tree.
I think that'd probably be the way to do it.
If you want to get those LLaMA changes into tree, that should be a separate PR.

##### **Hooved** [[00:50:03](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3003)]
Right, yeah.
I mean, the LLaMA stuff is pretty much ready.
I'm done working on that.
If by tree, you mean like the main tinygrad directory.
Yeah, I'm not moving anything there in this PR and this bounty.
I just had a lot of redundant logic for exporting model that was outside of export model.py.
So I'm just moving it in.

##### **Geohot** [[00:50:27](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3027)]
Yeah, cool.

##### **Hooved** [[00:50:28](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3028)]
OK.

##### **Chenyu** [[00:50:32](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3032)]
So ONNV, I will review that PR.

##### **Chenyu** [[00:50:41](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3041)]
And I think for Contrib Ops, it makes sense if the comma is using it or a lot of popular models are using it, then sure, we support those.
But it's the same thing as I think
That's why we want to have this script, so we know what Contrib Ops are really used.
And then we can decide what to do with those.
If we need to implement it, we implement it.
It's no big deal.
But since there can be a lot of undocumented and weird stuff, I think it's always good to know what we're working with before committing to working with those.
OK.
Otherwise, George does all the quantized stuff, ONNX stuff, look good to you from the ONNX side?

##### **Geohot** [[00:51:42](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3102)]
I mean, there's that bug in it.
Is there a fix to that?

##### **Chenyu** [[00:51:46](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3106)]
I don't know which one.

##### **Geohot** [[00:51:50](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3110)]
There's subtle differences in the rounding mode.
I don't know.
It's fine.
As tests pass, it's fine.
But there's a lot of extreme subtleties around things like, is the minimum value negative 128 or negative 127?
Is the rounding round to zero?
Or is it just, is it round to zero?
Or is it round even?
Like little things.

##### **Chenyu** [[00:52:23](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3143)]
I think we match.
You mentioned that we match ORT and now the spec.

##### **Geohot** [[00:52:28](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3148)]
I think that's probably the right idea.
Yeah, I'm going to pin the behavior or quantize to ORT.
I think that's right.

##### **Chenyu** [[00:52:34](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3154)]
OK.
Sounds good.
Sounds good.
Yeah, there is very little we can do with this if the popular implementations are different from specs, I think.
It is what it is
So I'll do this.
OK.
Moving on to other bounties.
Our thing was retinanet.

##### **Flata** [[00:52:56](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3176)]
Hi.
So last week, I spent most of the time tracking the NAN issue with the loss.
I was kind of worried about between the classification and the regression loss causing different issues, but I was able to boil it down with the power gradient thanks to Chen Yu on that.
Yeah, so I'm going to give it a try today to see if everything works out.
And then I'll also do some benchmark runs to get the correct run started this week.
So that's what I'm hoping for.

##### **Chenyu** [[00:53:32](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3212)]
Sounds good.
LLVM speed?
I don't know if this person is here, but there are.. 
is typing.
Is that you?
We can grant you speaker role.

##### **Geohot** [[00:54:06](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3246)]
You have speaker role.

##### **Chenyu** [[00:54:10](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3250)]
You need to leave and rejoin the meeting, then you can speak.

##### **Chenyu** [[00:54:17](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3257)]
B1 TGI also gave you speaker role.

##### **B1TGI** [[00:54:24](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3264)]
Hello.
Okay.
Hi.
So, yeah, I was just an update on that test some yellow or green on Macs with LLVM.
So I have a group opt-op working for the CPU backends, Clang and LLVM.
But I realized that it's breaking CI because of, well, for the most part, it's because when we're estimating the flops on things like Arange or other operations, when it applies the grouped opt-up, it was inflating the flops non-linearly.
So I realized there was a slight bug in how I implemented it, so I fixed that.
And now there's still a problem with the estimation, but I think it might be in the estimator, but I'm not sure.
So I'm kind of investigating that, but I think I'm on the right path to having this.

##### **Chenyu** [[00:55:13](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3313)]
Are you sure it's the estimation that's wrong, or is it really..
So because Arange has its own rewrite rules that optimize the Arange and friends to the simple form, and if that's broken, there is an issue that groups can break Arange.
But if it's applying group, then the rewrite rule doesn't apply anymore.
Then it would degrade to the slower version of Arange.
But it might not just be estimation.
It might be the underlying actual kernel becomes slow.

##### **B1TGI** [[00:55:50](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3350)]
OK, yeah.
To answer the question, no, I'm not sure.
So I will look at that and see if it's just one.

##### **Chenyu** [[00:55:55](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3355)]
If I was going through four, you can see the code.
And it's pretty obvious.
You see that if the Arange has one more for loop to it, then that's broken.

##### **B1TGI** [[00:56:05](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3365)]
Yeah.
And that might be it because I was, oh, sorry.

##### **Chenyu** [[00:56:10](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3370)]
No, no.
If that's the case, you can just talk about this somewhere in the channel.
And I don't think that's directly related to the bounty.
But it needs to be solved before this is supported.

##### **B1TGI** [[00:56:27](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3387)]
Yeah, that makes sense.
Yeah, I was still just going down, just starting to go down this rabbit hole at the end of last week.
So I will explore more and see exactly where the problem is, and I'll update in general.

##### **Chenyu** [[00:56:40](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3400)]
Sounds good.
OK, I don't know what's suppressed, but B1T1G should be able to talk.

##### **Chenyu** [[00:56:55](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3415)]
Suppressed.
I don't know what that means.
I don't know.
Try leave rejoined.
If you cannot talk, you can type.
Then we figure this out before the next meeting.
Yeah, I don't know if suppress is a thing on our side.
I don't know.
OK, that's how we figure all the technical issue.
Let's talk about rewrite speed.

##### **Ttomsa** [[00:57:49](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3469)]
I wanted to talk a bit, I think, more than just the implementation.
The variable binding is fundamentally incompatible with tree automata, which means that we need to do the variable binding in a separate pass.
It can't actually be incorporated into the state or the match.
This makes it substantially slower.
For example, about
So the test that I'm doing is running symbolic 2.0 after the vectorize, because that's by far the slowest part of the graph rewrite.
And about 50% of the bindings fail, and 50% succeed.
But the failures are five times slower than the successes.
And that's because we have a lot of generic patterns that will match a lot of stuff.
We have a lot of patterns that are big and are just preoccupied with finding the equalities.
So finding the patterns that match, for example, two instances of X. Because that's the way to filter out whether the patterns match or not.
And because the variable bindings are not part of the state, those types of patterns will run every time.
and they're very slow.
I tried to do some pre-processing to speed that up, and I did speed it up by three times instead of being five times slower.
It's three times faster than that.
But it's still pretty ugly.
It's very ugly.
And that would make it so that, OK, the 4x speed is possible, but it is very ugly.
So I was, I guess I also wanted to say,

##### **Geohot** [[00:59:32](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3572)]
I think the idea with that is not to think about it as a variable, but just think about it as an equality constraint.
You can completely separate the idea of variables from an equality constraint.

##### **Ttomsa** [[00:59:43](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3583)]
Yeah, so that's the pre-processing I did.
I essentially just, I didn't actually, I tried to speed it up by just checking the equalities at the sort of necessary positions for each pattern.
But even that, it's..
So, for example, there's something called the consistency automaton, which does that.
It interweaves states with equality constraints.
So it will have an extra sort of step.
But I don't know if that would be much different than what I'm doing, which is sort of doing it.. Because fundamentally, you would always have to do the equality constraints.
It doesn't actually.. You cannot.. You can't
put that information into the transition function.
For example, if we have ops.const.

##### **Geohot** [[01:00:33](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3633)]
You're going to have to track binds.
You're going to have to track your, it's not, I mean, you still put it into the automata.
You just have this external thing where it binds to a special place.
But it doesn't have to be names or anything.
It doesn't have to be the variable names.
This could be a completely separate thing.
Like right now, one of the things that makes it slow is that we bind the variable names regardless of whether the pattern ends up matching.
And we don't have to do that.
We just extract the ones that are equality constraints and only bind them if it's an equality constraint.

##### **Ttomsa** [[01:01:11](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3671)]
We would have to bind it to actually run the functions, right?
Whether there's constraints or not, you actually need to bind them at some point to actually run the function.

##### **Geohot** [[01:01:23](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3683)]
Well, yeah, but you can bind the names way late.
The equality constraint can be handled as a completely separate thing.

##### **Ttomsa** [[01:01:31](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3691)]
That is what I'm doing.
The bindings are not part of the state.
In fact, they can't be part of the state.
What we would like is to be able to.. The reason why there's such a potential for speed is that the vast majority of UOps match sets of patterns that already sort of match
Essentially, we're reusing a lot of the computation, but we're already doing that.

##### **Geohot** [[01:02:02](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3722)]
I think we should discuss this on a PR.
I think put up a PR with this stuff, and then we'll discuss it there.

##### **Ttomsa** [[01:02:08](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3728)]
I think you can just look at the code of that PR, because I had the valid binds.
I had something called valid binds.

##### **Geohot** [[01:02:14](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3734)]
Why aren't the tests passing?

##### **Ttomsa** [[01:02:18](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3738)]
Wait, why?

##### **Geohot** [[01:02:20](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3740)]
Why aren't the tests passing?
Oh, it's just linters and stuff.
Everything else works.

##### **Ttomsa** [[01:02:27](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3747)]
No, but it's not integrated.

##### **Geohot** [[01:02:30](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3750)]
Yeah, yeah, yeah.
You've got to integrate stuff.
You've got to integrate it, make it slow, and then we can talk about how to make it fast.
Correctness, then speed.

##### **Ttomsa** [[01:02:41](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3761)]
No.
So it already, I have a very good sort of sense of what.

##### **Geohot** [[01:02:46](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3766)]
Correctness, then speed.

##### **Ttomsa** [[01:02:47](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3767)]
It is working.
That's not the issue.

##### **Geohot** [[01:02:49](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3769)]
OK.
Make it work.
Pass the tests.
Correctness, then speed.

##### **Ttomsa** [[01:02:54](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3774)]
Okay, so the point that I guess I'm trying to get at is that it doesn't matter because it will be slow.
It doesn't matter to try and improve correctness.
I'm saying that it will be slow.
No, there's no way to speed it up.
So what you were saying about the variable bindings, that it's just consistent checks, I already did that, right?

##### **Ttomsa** [[01:03:12](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3792)]
I didn't catch that.

##### **Geohot** [[01:03:17](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3797)]
We'll discuss this on the PR.

##### **Ttomsa** [[01:03:21](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3801)]
OK, so can I talk about egrefs?
I wanted to talk about egrefs.

##### **Geohot** [[01:03:25](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3805)]
No, no, no, no.
OK, let's move on.
Yeah, with this, again, it's hard to have a discussion.
With all of these kind of things for these bounties, and I should really be more strict about it, first get something that is correct, and then we can discuss speed.
And if you say there's no fundamental way it can be fast, well, then it's not eligible for the bounty, right?
But I do think the solution to this is something that is a just, yeah, it's an automata and you have state that does the equalities.
There's no way around that.

##### **Chenyu** [[01:04:16](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3856)]
Yep.
I think if you want to discuss about eGraph, at least you write something up.
We know this as a term for a while, but either you have a prototype or at least you have some written proposal.
Otherwise, it's very hard to discuss about new concepts or new algorithms.
OK.
Final stuff for lykles.
know which one you are actively working on so i just put a place over there you want to talk about something uh if no we can also just discuss on the pr i see you close some of the loader ones and reopen a new one so we can discuss there as well
OK.
Is that all?
Do I miss anything?
Anything on your mind, George?

##### **Geohot** [[01:05:33](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3933)]
Particularly.
Mostly just excited about the torch backend.
I hope it starts making progress.
I hope this is the kind of thing I saw.
Cortis made some good progress in the torch backend.
Yeah, and I'm down to continue to put more bounties up for that as those ones get solved.

##### **Chenyu** [[01:06:05](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3965)]
The amount you put now?

##### **Geohot** [[01:06:11](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3971)]
Well, we have two bounties now.
We have a $200 one for the MNIST one and a $200 one for the ops test.
Yeah, then I think, yeah, we can have another one for CIFAR.
We can have one for multi-GPU working.

##### **Chenyu** [[01:06:36](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3996)]
Why is CIFAR not working with test ops pass?

##### **Chenyu** [[01:06:39](https://www.youtube.com/watch?v=Dm83mY6ONks&t=3999)]
Oh, we'll see.

##### **Chenyu** [[01:06:43](https://www.youtube.com/watch?v=Dm83mY6ONks&t=4003)]
Cool.

##### **Geohot** [[01:06:44](https://www.youtube.com/watch?v=Dm83mY6ONks&t=4004)]
I'm not sure how much TestOps tests all the kinds of indexing stuff.
I don't know how good our scatter and gather are.
Maybe they work.

##### **Chenyu** [[01:06:52](https://www.youtube.com/watch?v=Dm83mY6ONks&t=4012)]
I mean, we have a separate test for indexing, but I think the ones for scatter and gather in TestOps are pretty comprehensive.

##### **Chenyu** [[01:07:04](https://www.youtube.com/watch?v=Dm83mY6ONks&t=4024)]
Cool.
OK, sounds good.
that's all and thanks everyone see you next week
