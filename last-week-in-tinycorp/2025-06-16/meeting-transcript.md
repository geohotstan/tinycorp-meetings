# 2025-06-16 Meeting

### Meeting Agenda

**Time:** meeting #75, 9am Monday San Diego time
- company update
- TestGrad / scheduler
- MLPerf LLaMA 405b, BERT grad accumulation, LLaMA 405b inference
- viz tooling
- drivers
- cloud, hash, tinyfs
- Z3 symbolic
- ONNX (parser merged!)
- local
- other bounties (RetinaNet, lm_eval, AMD_LLVM, cloud sync stuff)

### Audio

[Youtube Link](https://www.youtube.com/watch?v=MXDfAfrJmrQ)

### Highlights

- **[Company Update](#geohot-000005)**: AMD contract discussions are complicated; uncertain if AMD is serious. If not finalized soon, might discontinue negotiations by next Monday.

- **[TinyBox Cases](#geohot-000420)**: TinyBox cases shipped via DHL and FedEx, some expected shortly. Additional shipment arriving July 5th by sea. Boxes will start shipping this week.

- **[Red Box Sales](#geohot-000620)**: Two red boxes sold likely to a government-related buyer, only two remaining. Green V2 has more than double the flops of Red.

- **[TestGrad Development](#geohot-000914)**: Significant progress; kernel.py removal simplifies complexity. New scheduler handles views better. Aim to integrate entire MNIST into one function without CPU graph.

- **[Kernel Splitting and Scheduling](#geohot-001331)**: Clarified kernel splitting logic using global barrier (GBarrier) instructions. CPU kernels could now be a single large kernel.

- **[BERT Gradient Accumulation](#chenyu-001753)**: Adding gradient accumulation to BERT and investigating 3x memory usage issue; aiming to test and submit multi-machine training for next MLPerf run.

- **[LLaMA 405B Inference](#chenyu-001933)**: Plans to run inference tests on AMD MI300X; downloading weights in progress.

- **[Visualization Tooling](#qazalin-002018)**: Perfetto replacement nearly ready for merge, significantly faster and simpler. Still reviewing necessary features to ensure parity.

- **[NVIDIA Driver](#nimlgen-002555)**: NVIDIA driver nearly complete; GPT-2 compute working. Refactoring PCI interface and HCQ to improve clarity and reduce inheritance complexity.

- **[Cloud Filesystem Manager](#wozeparrot-003046)**: Filesystem manager progressing; handling chunked uploads and managing file distribution across machines.

- **[Symbolic Expansion and Division](#geohot-003309)**: Evaluating symbolic expansion and integer division behaviors. Considering defining Tinygrad division semantics clearly, potentially influenced by hardware specifics.

- **[ONNX Parser Merged](#geohot-003509)**: ONNX parser integrated; debugging ongoing occasional segmentation faults and file handling in runner.

- **[Local Memory Masking](#ignaciosica-003719)**: Working on local memory masking; clarifying issues regarding broadcast and local dimension handling, important despite upcoming TestGrad changes.

- **[RetinaNet Bounty](#wozeparrot-004802)**: Ongoing efforts on evaluating RetinaNet with Tinygrad; facing challenges replicating Torch operations, proposing necessary Tensor functions.

- **[AMD LLVM Update](#chenyu-005303)**: Default compiler switched to AMD LLVM, yielding a slight (~1%) performance improvement on ResNet compared to ROCm.

- **[Remote Multi-host](#nimlgen-005703)**: Basic remote multi-host implementation reviewed; approved host specification format, potentially query-based device enumeration considered.


### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=0)]
Let's start with company update.

##### **Geohot** [[00:00:05](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=5)]
Yeah, more back and forth on the AMD contract.
I think we'll talk about it in this meeting.
You know, it's just it's so difficult to work with these people.
It's like, is this a priority for you or not?

##### **Geohot** [[00:00:19](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=19)]
You know?
Okay.

##### **Geohot** [[00:00:28](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=28)]
Yeah, I mean, I don't know.
We'll see if that happens.
But yeah, I don't think we should spend too much time thinking about.. The contract would be for 405B LLaMA on AMD's new hardware.
You know, if they come through with it.
But it's just so.. It's so like.. You don't know anything about what's true.
They don't show you any of their.. Now it's in legal review.

##### **Geohot & Chenyu** [[00:00:53](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=53)]
Like, what?
Chenyu: Yeah.
Geohot: Why?
I don't get it.
What does this have to do with legal?
Chenyu: Of course it has to do with legal.
Geohot: Why?
We're not getting anything.

##### **Geohot** [[00:01:13](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=73)]
Something I'm really concerned about in general is you never want to.. You see so many people.. This is how I feel about using React and Kubernetes.
If you use these things, you become Meta or Google.
The app's a [Trojan horse](https://en.wikipedia.org/wiki/Trojan_Horse).
And this sort of mentality is a Trojan horse too.
You start thinking about it and interacting with this kind of thing.

##### **Geohot** [[00:01:41](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=101)]
And then you just become this.

##### **Chenyu** [[00:01:46](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=106)]
I think having a lawyer looking over your contract makes sense.

##### **Geohot & Chenyu** [[00:01:50](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=110)]
Yeah, sure, but like..
Oh, you know, I'd say legally, I don't know.
I don't know.
So I'm lowering to a 50% chance this contract goes through.
Chenyu: No, I think legal review is pretty serious.
I'll give you a higher chance if it's really like just a legal review.
Geohot: But is it even true?
Like?

##### **Chenyu & Geohot** [[00:02:10](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=130)]
Of course.
Geohot: Maybe. I don't know.
Okay, anyway, we should we should get we should see if this is happening anyway soon.

##### **Geohot** [[00:02:23](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=143)]
Again, I'm this close to saying, no, when you guys are serious, come back and, you know.

##### **Geohot** [[00:02:31](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=151)]
Yeah, but that's.. I don't know.

##### **Geohot & Chenyu** [[00:02:36](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=156)]
Like, actually, when you're serious, come back to me with something.
When you're serious, here's my wiring info.
Wire me the money.
Chenyu: Yeah.
Geohot: No, it's just like, you don't want to start.. We don't need the money.
You don't want to start letting this behavior into your company.
Chenyu:I mean, it's not like we are doing legal review.
I understand.
I understand.
But, you know, really, really at arm's length.
Because, like, this stuff comes in and it just corrupts your company and you see how these things become so ineffective.
You know, I say that, like, my job at Comma is just to keep all the bullshit away.

##### **Chenyu** [[00:03:15](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=195)]
Yeah, but also Comma or Tiny is not a public company, right?
Uh,

##### **Geohot** [[00:03:21](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=201)]
No, but I mean, that's not even the point, right?
It's like, you want to do legal review, you do all that before you talk to me.
You know, that's your problem.
I don't want to hear about this.
Like, you come to me, you want a contract?
That's okay, you come to me with a contract.
Make it ready to sign.

##### **Geohot** [[00:03:37](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=217)]
Yeah.
Didn't we also ask for revision?

##### **Geohot** [[00:03:43](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=223)]
Well, yeah, but like, you know, we asked for like two lines to be changed.
It's been a week.
I just don't think they're very serious.
I don't think we're going to end up working with them.

##### **Chenyu** [[00:03:53](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=233)]
I see.
Okay.

##### **Geohot** [[00:03:54](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=234)]
Yeah.
No, I'm going to say, if this isn't signed, if the money's not in our bank account by next Monday, I don't think we should waste any more time thinking about this.

##### **Chenyu** [[00:04:03](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=243)]
Okay.
Yeah.
Did we get TinyBox cases?

##### **Geohot** [[00:04:10](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=250)]
No, we didn't get the TinyBox cases yet either.

##### **Chenyu** [[00:04:16](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=256)]
I heard it's in the mail.
It's not in the mail.

##### **Geohot** [[00:04:20](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=260)]
Well, okay.
There's two sets of cases in the mail.
There's one in the mail by DHL.
There's one in the mail by FedEx.
They were shipped on June 7th by DHL.
I don't know why there's no tracking number here, but it says ETA end of last week, which didn't happen, or the beginning of this week.
And then the other one, shipping by FedEx, I have a tracking number for, and it is in Memphis, Tennessee.
Chenyu: Great, sounds pretty close.
Geohot: Yes, it was in Memphis, Tennessee at 10.18 a.m., which is the future.

##### **Chenyu** [[00:05:01](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=301)]
We should have a resumed box delivery next week, if the case arrives this week.

##### **Geohot & Chenyu** [[00:05:09](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=309)]
Yes.
Yeah.
So we started building.
We got we got seven motherboard CPU RAM units tested.
We have all the GPUs ready.
So it's just the case.
But yeah, boxes should go out this week.
Boxes should go out this week and we should then be able to build like another 10.
And then once we have 10, I'll send out the email to the mailing list and I think they'll sell very quickly.
Imean, I know if I was buying something like this, I would wait till it's actually in stock.
Chenyu: Yeah. Then if it sells quickly, do we need more cases?
Geohot: Well, okay.
So we ordered 40 cases.
We have 10 coming in the DHL, 10 coming by FedEx, and 20 by sea that will be here July 5th.

##### **Chenyu** [[00:06:02](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=362)]
By 5th, okay.

##### **Geohot & Chenyu** [[00:06:05](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=365)]
Yeah, so we can sell 20 in the next two weeks.
No, we should be good.
Chenyu: Okay, sounds good.
Okay, we're still selling reds?

##### **Geohot & Chenyu** [[00:06:20](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=380)]
We sold two reds.
We sold two reds, and I'm 80% sure we sold them to the government.
So the government has been sending me emails through various different things trying to buy these.
And of course I tell them, no, I'm not filling out your supplier portal.
I'm not, oh, but you just need to certify that this is made in America.
I'm like, bro, I'm not certifying anything.
Okay, okay, but the least you could do is send us a W-9 and we're going to deliver a check to your office.
I'm like, no, you have to use the website.
So they eventually, this company bought it that looks like a front for the government or at least someone the government contracts with.
So I'm going to guess what happened is the government bought it through this company and then this company is going to charge the government an extra 20 or 30% using their process.
Chenyu: Interesting.
Geohot: Because who else is buying two red boxes?
But no, we legit sold two red boxes and they sent the wire, so they'll ship today.
So yeah, two red boxes left.

##### **Chenyu** [[00:07:22](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=442)]
Oh, only two left?

##### **Geohot** [[00:07:23](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=443)]
Only two left, yeah, and then that's it.

##### **Chenyu & Geohot** [[00:07:28](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=448)]
I just realized Green V2 has exactly double the flops than Red.
Geohot: It's exactly double?
Chenyu: That's what we.. No, more than double, I guess.

##### **Geohot & Chenyu** [[00:07:40](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=460)]
Yeah, I mean, the Green V2, like, originally I had a smaller number for the flops because I was going off of NVIDIA's datasheet, but NVIDIA's datasheet is just.. It's just funny that.. Like, I've never seen a company underpublish what the card is capable of so much.
The 4090 too is actually what it tests at.
Chenyu: Uh-huh.
Geohot: I don't know if it's like boost clocks or what it is.
But yeah, the red one is actually probably a little less than that.
I'm not sure you can actually get that number.
Yeah, I mean, I don't know.
You need like a canonical way to measure this.
There's flops, there's gemm flops.
But yeah, no, I think that the way we should measure it going forward for all the tiny boxes is whatever we can actually achieve with something like MMA Peak.
Similarly with RAM bandwidth, you have all these instructions.
You have to build it.
You build this benchmark using this special compiler, and then it gets high RAM bandwidth.

##### **Chenyu** [[00:08:53](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=533)]
You would need to disable some cache, maybe?

##### **Geohot** [[00:08:59](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=539)]
Yeah, no.
There's a bunch of kernel config things you can set.
It makes it faster.

##### **Chenyu** [[00:09:04](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=544)]
OK.
Sounds good.

##### **Chenyu** [[00:09:10](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=550)]
Let's move on to your [TestGrad](https://github.com/tinygrad/testgrad).

##### **Geohot** [[00:09:14](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=554)]
Yeah, so I think I'm making pretty good progress there.
The big difference between TestGrad and Tinygrad is TestGrad has no kernel.py.
So yeah, kernel.py is one of the oldest pieces of code in Tinygrad, and it's
It pushes a lot of complexity into the scheduler, where this complexity should just not be.
So currently in the scheduler, we can move views left and right.
But there's no actual reason to move views right, except for the fact that kernel.py needs them to look a certain way.
So the new scheduler only has view left.
It's the same view left that's in the other one.
And then all the views just pile up on expands.
And then the, and we can see if this can go on Tinygrad, but the key insight is that reduces make shapes smaller.
And the axes, like if you, an old reduce that would go from like 30-30 to 31, the 30 in position one and the one in position one are not the same axis.
Even though they're the same position, they're not the same axis.
And this is more elucidated in things like, imagine I have something that's 30-30 and 30-20.
I'm reducing both of them on axis 1, giving two things with a shape of 31, and then I'm adding them together, 30, 1, and then I add them together.
And that's correct, except currently, kernel.py can't express this, because the input shapes are different.
The input shapes are 30, 30 and 30, 20.
Yeah, that's basically why kernel.py has to go.
There's all these hacks in the arange fuser right now to detect this case and not fuse those aranges, but there's no reason at all you can't fuse those aranges.
So, yeah, the new one just doesn't have any of this.
It's very simple.
Fuse arange is the default.
So, yeah, it's probably going to be a few more weeks to actually get this integrated because with no kernel.py, we have no opt-ops anymore.
So, yeah.
I have to add the opt-ops back in, and I'm adding them in in a much more principled way, where every opt-op is pretty much doing some form of range splitting.
So you can just apply that to a graph.
You can just create the range node in the graph and then split the range how you see fit.
Like if you want to do an upcast on an axis that's 32, if you want to do like an upcast 4, okay, great.
Now it's a range of 8.
That range of 8 times 4 added to an upcast of 0, 1, 2, 3.
And you could do that as a rewrite rule instead of as a out-of-band kernel.py thing.
So it's really simple now.
Like, if you look at what's in CodeGenInit that does the kernel code generation, there's basically going to be another one of those for the big graph generation.
And then it's relatively simple.
I also want to make sure one of the goals of TestGrad is that it can generate
All of MNIST in a single function, and I want to remove CPU graph.
There's no reason with the CPU that you can't render the entire graph into one function.
Right now the only reason we can't do that is because it's unclear exactly how to even specify that.
I want to make sure there's a clear language to put
Huge things inside a single function.
And this works on the CPU because there is no G and there is no L. There are no global loops.
So yeah.
Just being more clear about when loops end, when loops begin.
This fixes the reduced thing as well.
So I have a clear language for it.
I just need to make it all work.

##### **Chenyu** [[00:13:23](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=803)]
And how do you, in the new world, how do you group kernels?

##### **Geohot & Chenyu** [[00:13:31](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=811)]
How do you decide what's in a kernel?
Chenyu:How do you decide when you need to split a new kernel?
So everything can be in one kernel, presumably, but then for different reasons, you might want to split into a smaller one?

##### **Geohot** [[00:13:48](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=828)]
Yeah.

##### **Geohot** [[00:13:51](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=831)]
There's a distinction between a global.. So we still have the GBarrier instruction.
The GBarrier UOp is the same as the barrier UOp, except it applies on a global level.
So for the GPU, GBarrier means a new kernel.
For the CPU, all it means is close all the loops.

##### **Chenyu** [[00:14:16](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=856)]
Oh, I see. Okay.

##### **Geohot** [[00:14:17](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=857)]
So yeah, it'll just close all the loops, and then it'll write that out to a thing, and then that's it.

##### **Chenyu** [[00:14:22](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=862)]
Oh, so on CPU, there won't be more kernel splitting.
It's always one big kernel.

##### **Geohot** [[00:14:30](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=870)]
You can do it that way.
Right now it still has the same logic, but I can write whatever as the logic.
There's advantages to kernel splitting because of deduping.
So right now the deduping still occurs at the kernel level, and it might always occur there.
Yeah, if you're calling the same layer, right?
Because imagine rendering a transformer, it's going to render literally every layer as separate code instead of calling into the same thing, so..
There's advantages to this hierarchical structure, but really what you want to do is you want to put a range UOp in the overgraph to deal with the layers.

##### **Geohot** [[00:15:14](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=914)]
If I have an LLM with 10 layers, that should be a range.

##### **Geohot** [[00:15:26](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=926)]
But yeah, it's good.
It really clarifies what these things mean.
So what GBarrier means is close all of the loops.
In the same way, Barrier is basically the same thing.
Barrier means close all of the light blue loops.

##### **Geohot** [[00:15:49](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=949)]
GBarrier means close all of the blue loops.

##### **Chenyu** [[00:15:56](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=956)]
Close as in sync, like wait until every loop is done?

##### **Geohot** [[00:16:01](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=961)]
Yeah.
So in C, you can think of it as closing the loops.
On a multithreaded machine, you can think about that as a sync.
It just basically means that you're ending the scope so that this entire array must be materialized before you can move on to the next instruction.

##### **Geohot** [[00:16:28](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=988)]
Actually, that's interesting.
Maybe it should just be one barrier instruction that says up to what axis number you have to close.
So GBarrier would be barrier 0, and LBarrier would be something like barrier 2 or 3.

##### **Geohot & Chenyu** [[00:16:52](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1012)]
But I don't know.
Chenyu: OK.
Anyway, that sounds like good progress.
That's it?
Geohot: I think so, yeah.

##### **Geohot** [[00:17:11](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1031)]
I mean, that's basically the only change.
This week, I'm going to figure out how to start adding ops back in, having the kernels.
Also, beautiful MNIST doesn't work.
I still have to look into that.
All of the ops tests are passing except for the ones with zero shape, which I have to think about what that actually means.
I think those are things where we basically have tests for it, and then we just put hacks in a few places to deal with it, and it should just be dealt with in one place.

##### **Chenyu** [[00:17:49](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1069)]
OK.
Sounds good.

##### **Chenyu** [[00:17:53](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1073)]
Okay, let's move on.
We may or may not have LLaMA-405B.
Something I already tried before was to add grad accumulation to BERT.
I think we are interested in making sure this works anyway.
I plan to add that to BERT and to test that, which means something about BERT needs to be fixed.
BERT is using 3x memory now.
Not exactly sure why.
That was my plan this week.
Or at least to understand what's causing that and see if it's effective.

##### **Geohot & Chenyu** [[00:18:34](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1114)]
We definitely have to fix BERT.
I mean, it's just a question.
Look, if we don't get the AMD contract.. 
Chenyu: We are still going to work on BERT and submit BERT next run anyway.
Geohot: Absolutely.
And what I'd really like to submit for BERT next run is training on multiple machines.

##### **Chenyu** [[00:18:52](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1132)]
Great.

##### **Geohot** [[00:18:53](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1133)]
Yeah, multiple machines.
Let's figure out what the right gradient accumulation is.
Maybe we can start doing big steps.
A lot of those tricks still make sense.
It's just like, you know, I don't want to deal with like AMD's weird hardware.
Yeah.
I don't know.
It's a shame.
It's a shame how difficult, again, like, why don't these companies just make it easy?

##### **Geohot & Chenyu** [[00:19:17](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1157)]
Like, do you want to do this or not?
You know?
Chenyu: I don't know.
We'll see if that goes through.

##### **Chenyu** [[00:19:33](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1173)]
On a separate note, I want to see if we can run LLaMA 405B inference.
So I think Wozeparrot was helping me download the weight on MI300X machine.
I was hoping, I don't know if the memory bug is there, but it should be fairly easy for us to like split into eight GPUs and just run a few tokens.

##### **Chenyu** [[00:20:09](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1209)]
That's it.
With that, we can move on to VIZ tooling.

##### **Qazalin** [[00:20:18](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1218)]
I think I got one round of review from you, George.
It's in a good spot.
I tested on a full BERT run and it was pretty responsive.
I'm thinking we can merge it.
It's a little more lines than the UOps viz is because I'm not using any libraries and stuff.
It's just literally.. 

##### **Geohot** [[00:20:41](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1241)]
So, I mean, to ask the question if we can merge it, right?
So I really like that it's the default, that it just shows up.
Are there any downsides, right?
Like, I don't want to have a flag to turn it off.

##### **Geohot** [[00:20:59](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1259)]
We have to move away from flags.
It's overhead?
No overhead.
Great.
Yeah, I'll test it today and give you some more feedback.
Qazalin: I'll wait for that before merging.
Geohot: Cool.
How many lines is it?

##### **Qazalin** [[00:21:28](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1288)]
153 lines of JavaScript.

##### **Geohot** [[00:21:32](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1292)]
153 of JavaScript.
Any lines of anything else?

##### **Geohot** [[00:21:34](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1294)]
Or just JavaScript?
It's not too bad.
Cool, yeah, I'll test it out today.
Oh, and also, wait, do we delete Perfetto?

##### **Qazalin** [[00:21:46](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1306)]
Yes.

##### **Geohot** [[00:21:48](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1308)]
Okay, it deletes Perfetto.

##### **Qazalin** [[00:21:50](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1310)]
It doesn't, it doesn't, it deletes the button.

##### **Geohot** [[00:21:52](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1312)]
You can still go to slash profiler.
Do you not feel 100% comfortable deleting Perfetto?

##### **Qazalin** [[00:22:00](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1320)]
I do, actually.

##### **Geohot** [[00:22:02](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1322)]
Great.
Then let's delete it.

##### **Qazalin** [[00:22:02](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1322)]
I did last minute just made the Perfetto UI match exactly with the flame graph style stacking.
That looks good.

##### **Geohot** [[00:22:18](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1338)]
Do we have lines like Perfetto?

##### **Qazalin** [[00:22:22](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1342)]
Lines on the grid, you mean?

##### **Geohot & Qazalin** [[00:22:25](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1345)]
So in Perfetto, when you click on a kernel, there's lines connecting to what its dependencies are?
Qazalin: No.
Geohot: Play with Perfetto a bit more and see if you're really confident that we've 100% replicated the features of it.
And then for every feature, I'm not saying we have to replicate it, but for every feature you should say, okay, this is outside the scope, this is something we should have too.

##### **Qazalin** [[00:22:57](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1377)]
Perfetto has a lot of things.

##### **Geohot** [[00:23:00](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1380)]
Yeah, Perfetto has a lot of things, right?
Many of which are useless for our case.
I mean, my biggest complaint about Perfetto, and the main reason I never used it, is you'd click on it and it would take 10 seconds to load.

##### **Qazalin** [[00:23:11](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1391)]
Yeah, it's much faster.

##### **Geohot** [[00:23:13](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1393)]
Sweet.
It's also not always on.
Like the minute you put something behind a button, nobody clicks it.

##### **Geohot** [[00:23:38](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1418)]
Okay.
Yeah.

##### **Qazalin** [[00:23:45](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1425)]
Giving it out there, anyone can go with VIZ equals one test it.
The first thing that opens up is this graph.
Beautiful MNIST or multi GPU.

##### **Chenyu** [[00:24:00](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1440)]
I will also test it.
I'm very interested in this.

##### **Geohot** [[00:24:06](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1446)]
Yeah, great.
Yeah, let's get this on BERT and ResNet and see if we can see what's left.

##### **Chenyu** [[00:24:13](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1453)]
Oh, so the BERT thing you posted was not with BEAM search, right?

##### **Qazalin** [[00:24:19](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1459)]
Yeah, just pure BERT.
Exactly.

##### **Chenyu** [[00:24:21](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1461)]
So that R is probably just a bad default.

##### **Geohot** [[00:24:29](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1469)]
And then we probably want to move the memory graph there, too.
I think it makes more sense to have it in a

##### **Qazalin** [[00:24:37](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1477)]
I think so too, like a shared time access and then you'll have everything.

##### **Geohot** [[00:24:41](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1481)]
Yeah, but no, I think we can totally, let's get it merged before then.
Let's first replicate Perfetto and then think about what more features we want.

##### **Qazalin** [[00:24:50](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1490)]
What are the errors and stuff that show the dependencies?

##### **Geohot** [[00:24:56](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1496)]
I mean, or you can say we don't need it, but either way we should, for every feature of Perfetto, we either need to say, yes, we're going to build this or no, we don't need it.

##### **Geohot** [[00:25:14](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1514)]
I remember the arrows being kind of useful.
I remember the arrows just kind of showing me, oh, hey, that's where this one's coming from.

##### **Chenyu** [[00:25:25](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1525)]
Yeah, and I think for specifically this, maybe just open an issue to track the features you already decided to add or not to add.
So people who have experience with Perfetto can take a look and comment on anything if it's missing.

##### **Geohot** [[00:25:46](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1546)]
Cool. Nice.
Let's move on to drivers.

##### **Nimlgen** [[00:25:55](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1555)]
Yeah, I'll also add a bit to Perfetto and dependencies.
I think we might want to change style because it's really annoying to generate dependencies right now for Perfetto.
And yeah, if we implement something similar, we can definitely just make it a lot simpler.
And yeah, so currently dependencies are only visible in graphviz, so you need to run with graph=1 to see them.
Yeah, so yeah, finished with NVDriver.
I mean, we got compute GPT-2 working right now.
So the missing thing was graphics context, and I spent quite a lot of time on this.
So yeah, but now it works.
So yeah, this week we definitely will merge it.
I've tested, and it looks fine on Ada.

##### **Geohot** [[00:27:01](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1621)]
Great.
Any progress on copy out speed?

##### **Nimlgen** [[00:27:06](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1626)]
Oh, really no.

##### **Geohot** [[00:27:09](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1629)]
Yeah, we got to get that done.
We got to improve the copy out speed and then profiling on the Comma devices, figure out why the USB is slow, because Comma can't really use it yet.

##### **Nimlgen & Geohot** [[00:27:25](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1645)]
Nimlgen: Yeah, okay.
Geohot: But cool, no, glad NVIDIA's almost done.

##### **Geohot** [[00:27:37](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1657)]
I think there's also some time to spend just refactoring the general driver stuff and HCQ stuff, making sure everything's in its right place.
Hopefully the NVIDIA driver will force some good refactors.
Like a lot of the PCI interface stuff is fairly generic PCI stuff, but then there's a bunch of hard-coded AMD stuff.
I always prefer instantiation over inheritance.
You have a choice when you have something like PCI interface.
You can either create a class that has an object inside the class called interface, which is PCI interface, or you can override PCI interface with AMD PCI interface.
I think it's generally cleaner to do it in the style of you have something like AMD device that instantiates something called PCI interface.
I think that that lends to better abstractions.
But yeah, no, I think, yeah, once NVIDIA is merged, I could sit down and do a review and say like, yeah, I think we should clean up a bunch of this stuff.
I think a bunch of the HCQ stuff is kind of like this too, where there's lots of overriding.
There's lots of inheritance.
There's lots of HCQ devices being inherited by the AMD device and the NVIDIA device, and it makes it kind of confusing to track through what really needs to be implemented here.
Overriding a class is fine if what you're doing is you're adding a bunch of parameters to it or two clear, 10-line functions.
But when you have one 600-line class and then you inherit that class and then make another 500-line class, that's pretty unreadable.

##### **Nimlgen** [[00:29:34](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1774)]
Yeah, I see.
Yeah.
Yeah, I think this week a lot of refactors for NVIDIA.

##### **Geohot** [[00:29:42](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1782)]
Cool.
But yeah, no, if you have the 600-line class and the 500-line class, that's fine.
I'd rather the 500-line class, instead of inheriting, creates an object.

##### **Geohot, Chenyu & Nimlgen** [[00:29:52](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1792)]
AMD device creates an object called PCI interface.
And then that object can be reused by NVIDIA.
Chenyu: That's it?
Nimlgen: Yeah, that's it for me.

##### **Chenyu** [[00:30:31](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1831)]
Great.
Is Wozeparrot there?

##### **Wozeparrot** [[00:30:35](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1835)]
Yep, yep.

##### **Chenyu** [[00:30:36](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1836)]
OK, your stuff?

##### **Wozeparrot** [[00:30:39](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1839)]
Hoping to get something up for file system this week.

##### **Wozeparrot** [[00:30:46](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1846)]
Mostly just working on file system manager right now, because currently we need something that
When the user uploads a file to, it chunks it and then determines which machine each chunk lives on.
I don't know if it is here.

##### **Geohot & Wozeparrot** [[00:31:13](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1873)]
What, you want to talk about the symbolic expand?
Wozeparrot: Yeah.
Geohot: Do you need it?
Wozeparrot: It's not just symbolic expand.
A lot of stuff.
So the other thing is our current symbolic seems to not support

##### **Wozeparrot** [[00:31:25](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1885)]
Like exactly what the variable batch size is doing.

##### **Wozeparrot** [[00:31:31](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1891)]
Because our symbolic is very shaped around how the LLM KV cache works, which is a lot of shrinking.

##### **Chenyu** [[00:31:46](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1906)]
OK.
So I think the best way to proceed is probably

##### **Chenyu & Geohot** [[00:31:52](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1912)]
Also open an issue, or add some tests, or things you think should happen.
At the same time, I don't believe variable batch size will block you.
I mean, you can just use variable batch size.
Geohot: Yeah, I think the test is the way to go here.

##### **Geohot** [[00:32:10](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1930)]
Just write some small tests.
That's it.

##### **Chenyu** [[00:32:23](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1943)]
So these are symbolic, similar stuff.
I saw he had a bunch of PRs this morning.
I reviewed it already.
So I think one big thing here is integer division is pretty annoying.
I think before we add more rules to like, I think adding rules to fix stuff or removing rules to fix stuff is always good.
But before we add yet another bunch of rules, we need to decide what's the division, which version of division we want to use, and what's the reason for that.

##### **Chenyu & Geohot** [[00:33:09](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=1989)]
And even if later we want to do the transcendental style rewrite ourselves to define the div behavior, we still need to decide and fully unify the divide Z3 is using, the divide Python is using, and it seems to be the C div that the current device is using.
Geohot: Yeah, agreed.
I think we should probably look into, like read like the RDNA3 spec, and we should look into what the hardware actually supports.
And whatever the hardware does is just what our divide should be.

##### **Chenyu** [[00:33:59](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2039)]
Sure. I mean, there's a argument that your IR might want to use a different one because it simplifies better.

##### **Geohot** [[00:34:11](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2051)]
Yeah, OK.
And then do like a late rewrite to write it to be the one the hardware does?

##### **Chenyu** [[00:34:15](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2055)]
Similar to what we are doing with the soft-max, right?
It's like we use add because that rewrites better.

##### **Geohot** [[00:34:22](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2062)]
Yeah.
OK, good point.
I'm open to that, if there's one that's clearly better.
I guess, yeah.

##### **Chenyu** [[00:34:31](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2071)]
For now, we kind of treat it as a lot of one-off case, just because we don't have a good understanding.
And I hope this project would help us understand this better, make an informed decision.

##### **Geohot** [[00:34:44](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2084)]
Great.

##### **Chenyu** [[00:34:49](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2089)]
I'll work with him.
Let's move on to ONNX.
So we merged the parser.
That's great.
Was that bounty claimed?
Because I saw it's still yellow.
I don't know if yellow means not paid or what the question mark is.

##### **Geohot** [[00:35:09](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2109)]
I think the question mark is green, though I do see some crashes sometimes.
I see some seg faults in ONNX, and I don't know why.

##### **Chenyu & Geohot** [[00:35:21](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2121)]
I also see that ONNX Runner.. I think sometimes maybe out of memory or something.
Geohot: I see this PR that says ONNX Runner file as an input.
Do we still need this?Need true spec parsing.

##### **Geohot** [[00:36:01](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2161)]
I don't know what that means.
Oh, yeah, that was Mike.

##### **Chenyu** [[00:36:06](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2166)]
Yeah, yeah, yeah.
I just got the reply.

##### **Geohot** [[00:36:13](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2173)]
Yeah, I don't understand why this model runner to model proto runner is being imported.
I don't think it should be.
This should just be ONNX runner should take in a file or a tensor the same way the rest of them do.

##### **Geohot** [[00:36:29](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2189)]
Yeah.
So I think let's go for this PR.
Great.

##### **Geohot** [[00:36:41](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2201)]
A little bit closer to getting ONNX copied into the main.

##### **Chenyu** [[00:36:47](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2207)]
The most recent LLVM ONNX error out in metadata.
OK, interesting.
OK, I would check the ONNX runner file thing again.
And hopefully, that should unblock you from all other ONNX stuff that we are excited about.

##### **Geohot** [[00:37:13](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2233)]
Do we have anything for Local?

##### **Ignaciosica** [[00:37:19](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2239)]
Hi.
Hello.
Yes, I've been mostly working on, still, the masking problem for shared buffers.
I kind of identified three different issues.
One, for example, being when you want to promote something to shared memory, you want to keep the access. Broadcast it.
You don't want to expand it and to share the repeated elements.
So that right now is only hinted in shared_permute.
But in process_acc, there is a test in process_acc.
And it's a propagated pragma.
For example, there is one case that propagates an if-guard in that case, but it's kind of manual and it's also brittle.
And I think it's the cause for many linearization, sorry, test failures in BEAM search.
And that is only for one case, but for shared memory, for generic LDS, there are many cases of that.
So that's one issue.
And I think I have two main concerns.
One main concern is that I don't know how useful it is to keep working on this, as it is not clear how much this whole infra will change in the near future due to the work being done in TestGrad.

##### **Geohot** [[00:39:10](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2350)]
It shouldn't change much.
I mean, sure, the actual implementation will change, but the tests won't.
Whatever logic you put in there, if the logic is good, I'll just copy and paste the logic into TestGrad.
It's the same thing with TensorCores.
Like, TensorCores and Locals will not be in.. So right now we have this function called getModifiedAST, which is basically like a hacky form of a graph rewrite.
Um, what I'm going to do for TestGrad is just move everything that's in getModifiedAST into rewrite rules.
But like, it's not like the logic will change.
So like getting locals working in, in Tinygrad does not have to wait for TestGrad.
I will just copy and paste.
If the logic is good and well tested, I will just copy and paste that logic into a rewrite rule instead of into a function, but it's the same thing.

##### **Ignaciosica** [[00:40:03](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2403)]
Okay, cool.
So then I, I, I mean, I.
I kind of talked a little bit about the issues here, but I'll post more findings on this masking issue later today as a progress report, because I think there are some interesting things to be addressed.
So yeah, if it's useful to keep working on this, I'll keep updating it.

##### **Chenyu** [[00:40:31](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2431)]
Yeah, so I think it's definitely useful.
We definitely want this picture more down the line.
The best way is the same as you discover the issue, you discover the kernel that would trigger the issue, add it as a test so that we know if we are correct or we are incorrect.

##### **Ignaciosica** [[00:40:55](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2455)]
Yes.

##### **Chenyu** [[00:40:55](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2455)]
The linearizer might change.
And for the better part, it probably fixed some of the bugs for local and mask.
Some of this is probably just hack around because we didn't have cases like this.

##### **Ignaciosica** [[00:41:11](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2471)]
No, I think most of the issue arise before linearizer.
But yes.
Well, some minor thing that I didn't know if it was worth also upstreaming because of this change in the opt-ops is that Upcast, I think it should be reserved for global dims.
Upcasting a local dim is the same as upcasting a global dim, but with extra steps.
And it does reduce the search space significantly, but it unfortunately also decreases the speed of some kernels found.
As upcasting a local dim right now is a way of breaking the locality of the BEAM search algorithm.
It allows it to
To perform optimizations earlier.

##### **Chenyu** [[00:42:16](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2536)]
It's like you upcast twice, then you do a swap on those two.
Probably the same effect.
Compared to you first upcast a big chunk and to local, then upcast from.
Part of it from that local.

##### **Ignaciosica** [[00:42:32](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2552)]
Yeah, I think it's equivalent.
And if you don't upcast locals, you can arrive to the same kernel, but with fewer opt-ops.
So it does reduce the search space.
But given the current algorithm right now, it might happen.

##### **Geohot & Chenyu** [[00:42:52](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2572)]
You're just going to have to test that, and we're going to need some way to test that, right?
Like completely, they're totally equivalent, right?
It does not matter if you upcast a global dim, then local a global dim, like upcast for local 32, right?
Or you could also local 128 and then upcast 4 on that local.
And those two kernels are equivalent, but just because the end kernels are equivalent doesn't necessarily mean that the search space is amenable to finding it.
So I'm open to changes like this, but we would need a way to benchmark it.
We'd need a way to say that, yeah, the search hits just as well, and it searches less of the space.
Just saying they're equivalent, therefore we should only do it one way,
Yeah.
I mean, you can't assume that you have a perfect search algorithm.
Yeah, but we.
Chneyu: I think it's more.
So we had been doing this for a while.

##### **Chenyu** [[00:43:50](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2630)]
If you can show that it's not off by too much and it indeed reduced the search space, I think that's more preferred.
Yeah, I mean.. It's not like we're on the line of, like, we have a frontier of search thing that we want to maintain.
As long as the memo looks fine, the batch size one transformer looks fine, like.. 

##### **Geohot** [[00:44:20](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2660)]
Yeah, yeah, yeah.
That's what I mean by a test suite, right?
Like, we should just make sure that we're doing fine on..
On all of those.
But yeah, no, I would think that what you actually most of the time want to do is you want to like you have a global dim, you first want to local it and then you want to upcast again on top of that.
Because the best way to memory coalesce is across the locals.
So my guess would be thinking about it more.
It's actually the other way.
It's not that you Yeah, I'm fine with I'm fine with if we tested on what we have, I'm fine with not allowing upcast on locals.
If you think about the dim globally, the thing that you actually probably want is globals upcast locals.

##### **Chenyu** [[00:45:10](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2710)]
Because you can decide, kind of start from your upcast, right?

##### **Chenyu & Geohot** [[00:45:13](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2713)]
That's your kind of a minimal element in your compute.
So you start, it's hard for search, but you really want to start from that, then build.
Geohot: Wait, no, I think you want to start from locals.

##### **Ignaciosica** [[00:45:26](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2726)]
Yeah, I think you want to start from locals too.
I mean, if you start from locals, your threads are contiguous, right?

##### **Geohot, Chenyu & Ignaciosica** [[00:45:35](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2735)]
Yeah, you want your memory to coalesce as much as possible.
So the ideal first step in most kernels should be doing locals on the thing that's stride 1, or the closest to stride 1.
Chenyu: I see.
Ignaciosica: If you upcast first, you can vectorize.
Geohot: Well, it's kind of counterintuitive.
Yeah, it's kind of counterintuitive.
Like you usually think, actually, no, this isn't probably, no, wait, no, no, no, no.
I'll correct this again.
It depends on your dtype.
So if your dtype is float, you probably want to do locals first.
But if your dtype is half, the first thing you want to do is upcast without a doubt.
Upcast two.
You want to upcast two.
Yeah, the first thing you're going to want to do is upcast two.
And see, that's the one that might miss.
Because the locals has a much stronger pull.
Yeah, yeah, yeah.
Okay.
Yeah, I would guess for half that you I bet you that's what I mean, yeah, what we really need to do is just have a way to like, like, say, like, okay, is this happening?
Right?
Like, what's the path taken to search?
I wrote some tooling around this, but it wasn't very good.

##### **Chenyu** [[00:46:53](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2813)]
Yeah, so there was a test somewhere that tried to do the BEAM search on kernel data sets and found some stuff.

##### **Geohot** [[00:47:10](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2830)]
This will be fun visualization tools to write.
We need to write tools that show how the search is happening.

##### **Chenyu** [[00:47:19](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2839)]
Basically, a way to have a script or tools that shows these hypotheses are indeed happening for search.

##### **Chenyu & Geohot** [[00:47:29](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2849)]
Chenyu: That might also give us better ideas for how search should improve.
Geohot: Yeah.
I wrote some bad graph tooling around it, but it would be great to get this integrated.
Maybe that'll be the project after time VIZ.

##### **Chenyu** [[00:47:44](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2864)]
Thank you.

##### **Ignaciosica & Chenyu** [[00:47:50](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2870)]
Thank you.
Chenyu: Okay.
Other bounties.
I don't know if we got any update for RetinaNet.

##### **Flata** [[00:48:02](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2882)]
Oh, hello.
Yeah, so I've been still working on the eval itself.
I think I'm halfway there.
It's just like I'm trying to find equivalent Tinygrad operations for, I think, well, unique I figured out already.
But there's some other ones that I'm still trying to figure out.
So I've been just updating my draft PR over time to make those changes.

##### **Chenyu** [[00:48:27](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2907)]
Yeah.
If you have the chance, you can also post some of these

##### **Chenyu** [[00:48:33](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2913)]
In the channel, I think similar to the moving CIFAR to Tinygrad one, I think there are some stuff that we currently don't support well.

##### **Chenyu** [[00:48:41](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2921)]
And it's also not clear how to write those.
And we might want to improve those, either like adding a corresponding tensor function if we don't have it,
Because we expect people to rewrite this Torch code or equivalent to Tinygrad.
Any blockers that you find would be helpful for us to improve.

##### **Flata, Chenyu & Wozeparrot** [[00:49:05](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2945)]
OK, sounds good.
Chenyu: OK, LM-Eval.
I don't know if Fancat can talk here.
Wozeparrot: I don't think they can.

##### **Geohot** [[00:49:21](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2961)]
Who?
Fancat, you're added as a speaker if you have to exit and reenter the voice chat if you want to talk.

##### **Geohot** [[00:49:45](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2985)]
You don't have to talk, it's totally up to you.

##### **Wozeparrot & Geohot** [[00:49:53](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=2993)]
SGLang is..Quite different.
Their prompt is different, but it seems they're prompting for a reasoning model.
It seems a little unclear.
Geohot: Oh, I tried to use Ollama this weekend for a project I'm working on.
Yeah, we can do so much better.
The most annoying thing, the thing that took me forever to realize, is it was like catting a file into it, and the default context length is 2048.
Wozeparrot: Oh, yeah, people complain about this all the time.
Geohot: And then there's no environment variable to set it.

##### **Wozeparrot** [[00:50:32](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=3032)]
No, you have to get it, the modelfile.

##### **Geohot & Wozeparrot** [[00:50:33](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=3033)]
Yes.
Which is crazy.
And then eventually I do it, and then it just starts taking forever.
I update the context to what the max context size is of the model, and then it's just sitting there hanging for three minutes, and I'm just like, wow.
There's no update on it.
There's no progress bar.
What is this doing?
How many tokens is my file?
How come it doesn't tell me this?
Like, yeah.
So I think there's actually..
Wozeparrot: Ollama is pretty bad.
If you use just base LLaMA.cpp, it's better.
It's just more annoying to work with.
Base LLaMA.cpp?
Yeah, because Ollama is just LLaMA.cpp.
Oh, I didn't realize that.
It's the same thing.

##### **Wozeparrot** [[00:51:14](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=3074)]
I mean, it's nice.

##### **Geohot & Wozeparrot** [[00:51:15](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=3075)]
They make it very easy to fetch models, but then you fetch models.
Wozeparrot: Well, other models are out of date as well.
Geohot: You fetch a model, and it doesn't tell you anything about the quantization of the model.
It's just called like Qwen 32 b.
Wozeparrot: You fetch like DeepSeek-R1.
It just fetches the 8B version.
But it's called DeepSeek-Coder.
Geohot: What do you mean the 8B?
It fetches the 8B version.
Oh, the 8 billion weights?
Distilled into like.. Yeah, yeah, yeah, yeah.
Yeah.
I don't know.
I think that we can do a lot better with this and we could become, if someone wants to put effort into this, the default way.
Just pip install Tinygrad and then it'll run in the LLM.

##### **Geohot** [[00:51:59](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=3119)]
It'd be great also to be able to, if we could fetch from Ollama's HTTP.

##### **Geohot** [[00:52:09](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=3129)]
Yeah, like the model repositories are hugging face because that's like a, like, you know, okay, why am I using Ollama?
Why am I not using Tinygrad?
We don't have an easy, I just don't even like know how to do it.
And this is like, yeah, we need to, so I don't know, back to tinygrad/apps.

##### **Chenyu** [[00:52:30](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=3150)]
OK, anyway, so I think we just want some comparable stuff.

##### **Wozeparrot** [[00:52:38](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=3158)]
Yeah, so I think we just copy SGLang.
Whatever SGLang is doing, I think we just do that.

##### **Chenyu** [[00:52:46](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=3166)]
OK. Anyway, for Fancat, I assigned the validation of the bounty to Wozeparrot.
So just let him know if you have any questions.
Great.

##### **Chenyu** [[00:53:03](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=3183)]
AMD LLVM, I merged the default to using AMD LLVM.
And I think, at least on ResNet, because we update LLVM version to 20, it seems to be faster compared to our old ROCm AMD.
Slightly, like 1% faster, but slightly faster.
That's pretty nice.

##### **Wozeparrot** [[00:53:32](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=3212)]
Interesting.
Because ROCm is LLVM 21.
LLVM is faster.

##### **Chenyu** [[00:53:39](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=3219)]
But I also heard ROCm 6.4 is faster.

##### **Geohot** [[00:53:46](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=3226)]
Well, yeah, 6.4 would be 21.
I don't think 6.2 is 21.
Oh, 6.3 might not be 21.
Yeah, we should try that one too.
I mean, it's nice that we support both, but overall it's just so much cleaner to just have it be LLVM.
It's real.
Oh, it turns out also, I was engaging with some guy on Twitter, there's a SASS, there's an open source SASS compiler now.

##### **Wozeparrot** [[00:54:08](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=3248)]
Yeah, the one in Mesa.

##### **Geohot** [[00:54:09](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=3249)]
The one in Mesa, yeah.
Mesa has their own UOps called NIR.
So there's a bounty for that if anyone's interested.
If anyone can get that wired up.

##### **Wozeparrot** [[00:54:20](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=3260)]
I think if you do that, it will support AMD, like Mesa's AMD output as well.

##### **Geohot & Wozeparrot** [[00:54:24](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=3264)]
Yeah, it'll support the ACO one, yeah.
Yeah.
Yeah, so I called the bounty both of them.
You could do either one.
Yeah, I'm curious how performant that is.
Wozeparrot: Pretty decent, I think.

##### **Geohot** [[00:54:39](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=3279)]
Yeah.

##### **Geohot, Wozeparrot & Chenyu** [[00:54:39](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=3279)]
And then even more, we need the infrastructure to support the separation of device and compiler.
Who is working on that?
I'm working on it.
I'm working on it.
You have to delete CPUGraph first.
CPUGraph breaks this.
CPUGraph breaks the whole thing.
The refactor itself is very mechanical and easy.
And I will do it once we feel good removing CPUGraph, which maybe I'll just do today.
And just say, okay, we're going to comment out the test suite.
Yeah, no one is using CPUGraph now.
Yeah, okay, great.
I'll just remove it.
Wozeparrot: CPUGraph breaks some stuff.
Geohot: There's a special rule in remote for CPUGraph.
It's just not.. It doesn't look like the other graphs.
WozeparrotL There's an open issue right now.
A lot of stuff, when you try to run it on CPU, without J=2, it just doesn't work.
Geohot: Oh, great.
Yeah, okay.
Well, it just got deleted.
Chenyu: Great.
Geohot: Best code is no code.

##### **Chenyu** [[00:55:36](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=3336)]
Great.
Okay.
Second time we say goodbye to CPUGraph.

##### **Geohot & Chenyu** [[00:55:41](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=3341)]
It really doesn't want to exist.
No, I mean, the real solution to CPUGraph is something that looks like a runtime.
It's something that looks like a GPU-style runtime implemented on CPU that does hyper-threaded dispatch.
This will also be Tinygrad's answer to multi-threaded.
Like, yeah, if you have a CPU with 32 cores, there's no reason that we can't use it the same way you use a GPU with basically 32 cores.
Chenyu: Oh, so it would be a multi-threaded dispatcher, I see.
Geohot: Yeah, yeah, yeah.
It'd be a threading dispatcher, right?
It's not like multi-GPUs, because the CPU does have a unified memory space.
But it would be the same way the GPU, when you have a G dimension, how it dispatches them to all the compute units on the GPU.
Well, we can write basically that on a CPU, and that will also be the answer to CPUGraph.
We have to basically write a PM4 parser for CPU, or determine whatever..
That's the thing we want to use.
And then we have a CPU command queue.
And then the CPU command queue is parsed by something that's running on every thread.
That's the right way to do this.

##### **Chenyu** [[00:56:55](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=3415)]
Great.
OK.
Lastly, so I think Uuuvn is not here.
Wozeparrot, do you have anything to say?

##### **Wozeparrot** [[00:57:03](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=3423)]
I didn't get to looking at remote multi-host last week, so I'll do it this week.

##### **Geohot, Chenyu & Wozeparrot** [[00:57:12](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=3432)]
OK.
Chenyu: Just making sure it's not blocked on us.
Geohot: We have something that we should be reviewing now?
Wozeparrot: You can look at basic remote mode.
Yeah, this one.
Geohot: All right, cool.
All right, so you got this?
Wozeparrot: Yeah.
Great.
Looks OK.
I don't know about the format for specifying the hosts.
It's kind of verbose, but I don't really see a better way to do it.
You look in the test.
You have to do this.
You specify one device times the amount of devices on the device.

##### **Geohot** [[00:57:45](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=3465)]
Where?

##### **Wozeparrot & Geohot** [[00:57:47](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=3467)]
At the top.
Yeah, right there.
Yeah, you specify like this host.
Geohot: Wait, that seems great.
I love that.
Wozeparrot; What?
Geohot: How do you want to do it better?
Wozeparrot: I don't know.
Yeah, that's what I mean.
Geohot: That's actually super nice with the *.
Okay.
Yeah, I like it.
I mean, how else are you going to say that there's.. Yeah.

##### **Wozeparrot** [[00:58:03](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=3483)]
Right?
Hard to see another way to do it.

##### **Geohot** [[00:58:05](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=3485)]
I mean, you could connect and query the devices.

##### **Wozeparrot** [[00:58:07](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=3487)]
Yeah, that was my thought.
It's like you don't actually have to specify how many devices are on it.
You just specify the hosts.

##### **Wozeparrot & Geohot** [[00:58:13](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=3493)]
Like, no, I don't see any other multi-framework that.. 
Geohot: Well, no, but I actually do kind of like that, because you could say, like, I want to put on four GPUs there and four GPUs there.
Yeah, I like this better.
I like it better, specifying on the client.
Well, you could also say that, like, okay, we'll have it just query the number of GPUs from the process, but then, I don't know.

##### **Geohot** [[00:59:03](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=3543)]
This is fine.
I like this.
It's also something that can always be changed.
Yeah.

##### **Chenyu** [[00:59:12](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=3552)]
Okay.
Great.
Sounds good.
Okay, that's it for this meeting.
Thanks, everyone.
See you next week.

##### **Geohot** [[00:59:22](https://www.youtube.com/watch?v=MXDfAfrJmrQ&t=3562)]
Thank you.
