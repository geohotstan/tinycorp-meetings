# 2026-06-08 Meeting

### Meeting Agenda

**Time:** new meeting #23, 6/08 9am Monday San Diego time
- company update
- llama training
- VIZ
- hcq2
- CI and tests
- renderer refactors
- CONST, mixin
- bounties, issues, comma happiness


### Audio

[Youtube Link](https://www.youtube.com/watch?v=8Lfha_DNm7A)

### Highlights

- **[Company Update](#geohot-000010)**: Tinygrad is making money selling tiny boxes, and Geohot says the project has entered a “refining, not exploring” phase focused on core correctness before applications.
- **[Sales Growth](#geohot-000139)**: Sales are up 250% this year, the AMD contract is going well, and the company is choosing refinement over chasing immediate user-facing applications.
- **[Spec Over Line Count](#geohot-000318)**: Geohot argues that correctness and matching `spec.pdf` matter more than reducing lines of code; line reductions should come from removing unnecessary concepts, not trimming existing code.
- **[LLaMA 70B Convergence](#wozeparrot-000505)**: The 70B run was killed because it was not going to converge; tensor-wide and column-wise FP8 scaling were not enough, so the next test is block-wise MXFP8.
- **[405B Strategy](#chenyu-000613)**: Chenyu says 70B should serve as a smaller proxy for 405B, so they should apply the same techniques expected to be needed for the final 405B solution.
- **[VIZ / AMD Trace Progress](#qazalin-001001)**: Qazalin moved the AMD trace into VIZ format and improved runs from 3h20m to 2h50m, with remaining losses mostly from launching about 3× too many kernels.
- **[Copy Kernel Bottlenecks](#qazalin-001115)**: Many extra kernels are dumb copy kernels caused by reshapes, custom kernels, calls, all-to-all, shrink copies, and contiguous boundaries that happen too early.
- **[Standalone Repros Needed](#chenyu-001726)**: Chenyu asks for smaller standalone scripts that expose the extra-copy/all-to-all problems without needing to run the full LLaMA workload.
- **[HCQ2 Command Buffers](#nimlgen-002009)**: HCQ2 now has dependency tracking, mergeable queues, and initial command-buffer encoding into instructions, which is intended to replace the graph path.
- **[HCQ2 + JIT Gap](#nimlgen-002439)**: HCQ2 does not work with JIT yet because JIT uses params instead of buffers; the missing piece is encoding buffer addresses into a CPU buffer for submission.
- **[CI and Test Speedups](#chrism-002535)**: Linux tests are faster, macOS remains slow mainly due to WebGPU and Metal model tests, and CI Docker images are being considered to avoid fragile install scripts.
- **[Renderer Refactor](#geohot-003442)**: The new renderer style removes `GEP`, `DEFINE_LOCAL`, `DEFINE_REG`, pointer casts, `dtype.vec`, and dtype pointers, leaving kernels closer to the spec with movement ops like `SHRINK`, `INDEX`, `STACK`, and `BITCAST`.
- **[CONST and Mixin Cleanup](#chenyu-004042)**: Chenyu removed const device, moved more `tensor.py` logic into mixins, and is working toward making Tensor a thin wrapper over UOps via `_uop` and `_wrap_uop`.
- **[Real Random Seed Bug](#chenyu-005459)**: A random seed reuse regression is confirmed as real, caused by ordering and dependency issues after preallocating buffers and changing the code style.

### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=0)]
First part is company update.

##### **Chenyu** [[00:00:05](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=5)]
Yeah, two basic things. The company is doing well.

##### **Geohot** [[00:00:10](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=10)]
Making money selling tiny boxes. So, that's good. And the second thing is I really feel like we've entered this new phase of the project where we really are refining and not exploring. So, that's cool. And I almost wonder what projects ever really get to this stage. Like, I wonder what projects ever get to the point where they can really say, "Okay, we have kind of all the concepts that we need. We just need to refine all of these concepts. And we have time to refine all of these concepts before we optimize them." Even when you look at the LLVM IR, it's like, it's not perfect. It's good. But it's clear that, like, they got critical mass to a point that they could no longer change the IR. And I want to make sure that tinygrad never gets to that point. Which I think is a different tradeoff than is made in, like, almost all software. So, I'm happy that we can still iterate on these very core things. And I feel like we've entered a new phase of the project. So...

##### **Chenyu** [[00:01:28](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=88)]
Great. Okay. Anything else?

##### **Chenyu** [[00:01:37](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=97)]
No. Nothing else.

##### **Geohot** [[00:01:39](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=99)]
I'll just say what I posted in the employees channel. Sales are up 250% this year. So, from a company perspective, we're doing well. From an AMD contract perspective, we're doing pretty well, I think. So, yeah. I mean, we're succeeding at all those things and hopefully the choices that we're making with refinement instead of applications are the correct choice. I think it is. I think it's cool that we get to do this and don't have to do this pursuit of applications like so many other software products have to do.

##### **Geohot** [[00:02:19](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=139)]
Like even to get at the, "has there been any work towards getting tinygrad running in Docker?"

##### **Geohot** [[00:02:29](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=149)]
I mean, we could do that. We could start saying, okay, here are the actual use cases. But I think we were really premature with a lot of that stuff, like a lot of the kind of documentation. I think the eGPU project has brought in nothing. Nothing but annoyance. It's good that Comma is using it. But I mean, just in general, I think we were... Yeah, we don't need users yet. We need refinement. We need everything to really match the spec. And then hopefully this ends up yielding speed. That's the hypothesis. It's a long bet. I think it's right.

##### **Chenyu** [[00:03:05](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=185)]
Great. Can we reduce the lines?

##### **Geohot** [[00:03:13](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=193)]
So, I'm less sure that matters.

##### **Geohot** [[00:03:18](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=198)]
I think that... I haven't been as careful as I used to be with lines. Because I don't think lines are really the correct... Lines are a good metric. But the real metric is making sure that we have no unexpected use cases. There's so many times in the past I found myself kind of thrashing. I found myself saying, okay, I don't really understand why that UOp is on that UOp. But, oh, I could just change this and then it works. Okay, fine. Especially when we get back to things like the old scheduler. And even now with rangeify, it's still... I did a few refactors where I'm still not sure if it's correct. I'm still not sure if it's the right thing to do. So, I think it's really important that we pursue correctness over line count. Like, accuracy of the spec. But, yeah, I think that could eventually yield line reductions, if that's what we choose to cash in on it. But, yeah, like line reductions... The problem with line reductions is they ask the question, like, given this code, what can I remove? Versus, why does this code even exist? Why do we have something called the expander that, like, processes each UOp? Like, that's crazy. So, hopefully we'll see it measured in line reduction. But what I'm more concerned with is making sure that the spec matches spec.pdf.

##### **Chenyu** [[00:04:49](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=289)]
Yeah, that sounds good.

##### **Geohot** [[00:04:55](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=295)]
Okay. Okay. Let's move on. Let's start with LLaMA.

##### **Chenyu** [[00:04:59](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=299)]
LLaMA training. And MLPerf, if there's any residual things on that.

##### **Wozeparrot** [[00:05:05](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=305)]
Yeah, so LLaMA training side. 70B. I killed the 70B run because it wasn't going to converge. I've been trying a bunch of convergence things last week. So, the main thing right now is that tensor-based scaling with a single scale is not enough for 70B. I don't think anyone really does this anymore. So, I tested column-wise scaling. That also seems to not be enough either. So, the next thing to test is what everyone has moved to, which is block-wise MXFP8.

##### **Chenyu** [[00:05:41](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=341)]
Is that what other people use for their 405B submission?

##### **Wozeparrot** [[00:05:46](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=346)]
Yeah. So, NVIDIA's 405B submission in FP8 is MXFP8.

##### **Geohot** [[00:05:55](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=355)]
Is what? Yeah.

##### **Chenyu** [[00:05:56](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=356)]
MXFP8. Block-wise FP8.

##### **Geohot** [[00:05:58](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=358)]
Oh, okay. So, just need to move to that. And hopefully, that fixes convergence.

##### **Chenyu** [[00:06:13](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=373)]
Yeah, I think the goal for 70B is to have a smaller version of 405B. So, I think if it's a technique we know we need for 405B, we should try that. Otherwise, I don't see value of doing something that just makes 70B work, but might not work for 405B again.

##### **Wozeparrot** [[00:06:35](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=395)]
Yeah. I mean, there's a lot of things that work for 80B. Like, tensor scaling works for 80B, but it doesn't work for 70B.

##### **Chenyu** [[00:06:46](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=406)]
I think we should just apply everything we know that people are using for 405B and do it on 70B, because 405B is the eventual solution. So, we can just do it on 70B. Yeah. And 70B is just before we figure out everything, we can have a scaled-down version of that.

##### **Geohot** [[00:07:03](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=423)]
Yep. Jerry, do you really just want to copy NVIDIA?

##### **Wozeparrot** [[00:07:08](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=428)]
Yeah. The annoying thing about this is NVIDIA's main submissions now are all FP4. Don't care. We just need to match them a year.

##### **Chenyu** [[00:07:19](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=439)]
Yeah.

##### **Qazalin** [[00:07:23](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=443)]
Cool.

##### **Chenyu** [[00:07:25](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=445)]
And here's the thing. Any difficulty you find while working on this in terms of the dtype we need to support or everything's just custom now and you just find a way to work it? Like how generic this would be?

##### **Wozeparrot** [[00:07:37](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=457)]
I mean, the main thing that MXFP8 needs is just the GEMM kernel.

##### **Geohot** [[00:07:44](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=464)]
Oh, okay.

##### **Chenyu** [[00:07:44](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=464)]
So it's like a flag and we just hard-coded.

##### **Geohot** [[00:07:48](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=468)]
Yeah.

##### **Wozeparrot** [[00:07:50](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=470)]
It's not a new dtype or anything.

##### **Chenyu** [[00:07:52](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=472)]
There's still FP8.

##### **Wozeparrot** [[00:07:57](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=477)]
Wait.

##### **Geohot** [[00:07:58](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=478)]
And do we use like the kinds of FP8?

##### **Wozeparrot** [[00:08:01](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=481)]
Like MXFP8 is still FP8 E4M3. It just, rather than a single scale for your whole tensor, you have a...

##### **Chenyu** [[00:08:09](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=489)]
And they use that for both forward and backward.

##### **Geohot** [[00:08:12](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=492)]
Yeah. It has to be a new dtype though because like it's not converted in the same, like the same binary bytes don't get converted to like FP32.

##### **Chenyu** [[00:08:26](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=506)]
What do you mean? Well, so how are you expressing that there's a scale?

##### **Geohot** [[00:08:31](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=511)]
You pass it into the kernel. It's a separate arg into the kernel. Oh, it's a separate tensor.

##### **Geohot** [[00:08:36](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=516)]
Yeah, yeah, yeah.

##### **Geohot** [[00:08:37](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=517)]
Okay. All right.

##### **Chenyu** [[00:08:37](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=517)]
That's fine.

##### **Geohot** [[00:08:38](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=518)]
Yeah, yeah.

##### **Chenyu** [[00:08:42](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=522)]
Okay, cool. And then MLPerf's side were good.

##### **Wozeparrot** [[00:08:48](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=528)]
I didn't know if we wanted to do the supplemental. I wrote a quick one anyways.

##### **Chenyu** [[00:08:52](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=532)]
I think two years ago you wrote the... I wrote that one and this time you write this one in between. I didn't put anything. Certainly I didn't. So I think it's whatever.

##### **Geohot** [[00:09:04](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=544)]
They sent me three emails about our supplemental being missing. So I think we should just give them something. Yeah, I gave them something.

##### **Chenyu** [[00:09:10](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=550)]
They do this every time and I always just ignore it. I mean, are you going to attend their marketing symposium online? Probably not. Oh, we don't.

##### **Wozeparrot** [[00:09:23](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=563)]
Oh, yeah. That's probably fine. Yeah. No one had complaints. It's good.

##### **Chenyu** [[00:09:31](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=571)]
Yeah. I mean, it's nice that we have a number. I think no one complained just because no one really experienced. Yeah. Yeah. We need to be mindful for our progress on this because our final trending round will take quite a bit.

##### **Qazalin** [[00:09:49](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=589)]
Yeah.

##### **Geohot** [[00:09:52](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=592)]
Cool. Sounds good. Anything else?

##### **Qazalin** [[00:09:54](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=594)]
Nope. Okay.

##### **Geohot** [[00:09:57](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=597)]
Let's move on to VIZ.

##### **Qazalin** [[00:10:01](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=601)]
I've been working again on LLaMA and matching AMD's trace. So I actually decided at the end of the week, end of last week, to move the AMD trace to the VIZ format. So now I can see exactly where we're missing stuff. Last week my runs were at three hours and 20 minutes. This week we're at two hours and 50. So we're a little better than what we submitted with. I think I have all the tooling to get the last bits out. It turns out it's not really like one silver bullet. It's death by a thousand cuts. Uh, 50% of the reason we have a mismatch with AMD isn't like a kernel being slow, it's that we're launching three times the kernels and that launch alone has overhead. So yeah, working through the kernels one at a time.

##### **Geohot** [[00:11:08](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=668)]
What are most of the other ones? Like are they just dumb copy kernels that are inserted or?

##### **Qazalin** [[00:11:15](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=675)]
Dumb copy kernels. Um, I worked a little bit on fixing those. Uh, yeah. Dumb copy kernels happen because you might have like a reshape and that reshape would implicitly cause a contiguous early on between two custom kernels.

##### **Geohot** [[00:11:37](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=697)]
Yeah, there's definitely a whole bunch of cases where rangeify is not removing copies that it could, especially with custom kernels.

##### **Qazalin** [[00:11:49](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=709)]
If you read my diff, I have a PR for it. Uh, I'm not sure. I'm just going to remove the custom kernel. You remove the E_ kernels from custom kernels. They're mostly removed. Uh, it requires changing the custom kernels because rangeify fundamentally doesn't control the indexing of those calls. Like it can't go and inspect the indexing. Uh,

##### **Geohot** [[00:12:17](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=737)]
I think we're adding contiguouses at the high level for the custom kernels that we probably don't want to. I don't know if that's what this PR does.

##### **Qazalin** [[00:12:30](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=750)]
This PR doesn't change that boundary. It's still the case that contiguous does create a boundary in custom kernel. It's just that it doesn't create a contiguous kernel.

##### **Geohot** [[00:12:48](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=768)]
I think you can get something that's pretty dumb where if you have a reshape, even if you have a reshaped realized tensor going into a custom kernel, I think that custom kernel will still add a contiguous. 100% It does. Those are the things that we need to enumerate all those cases and we need to just fix them. The right solution here is to add those contiguouses much later.

##### **Qazalin** [[00:13:15](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=795)]
Yeah. So that's custom kernel. Then there's also call. I think call creates a bunch of copies. You have to think about what does a param versus what goes into the copy and then input. And sometimes it creates a copy and then writes back to the original.

##### **Geohot** [[00:13:42](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=822)]
So yeah, there's all these little things. Uh...

##### **Qazalin** [[00:13:51](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=831)]
I've spent today working on all-to-all because all-to-all also is very slow. It has a bunch of kernels. And some of those kernels are just literally copying stuff. And those are real kernels. We need to copy things for all-to-all. But I think they can use the SDMA engine. The project for all-to-all, I'm working on it. All-to-all also creates this very slow kernel with all the branches that totally doesn't have to be written like that. Uh... So... You mean the cat kernel? Oh yes, the cat kernel.

##### **Geohot** [[00:14:31](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=871)]
Yeah, yeah. Sieds had something back in the day that was kind of working on this.

##### **Qazalin** [[00:14:38](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=878)]
If we have a nice way to... That's not a huge issue. There's bigger problems. Mostly copies. But yeah, that cat is also kind of...

##### **Geohot** [[00:14:49](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=889)]
Yeah. I mean, I think the long-term solution to that cat is that we need to fix pad to pad to invalid and not to zeros.

##### **Qazalin** [[00:14:58](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=898)]
Yeah.

##### **Geohot** [[00:15:00](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=900)]
Um... It's not that padding to zeros can't be detected and folded out. But if you pad to invalid, the loop just kind of shouldn't go there. And then I'm sure it's not just the cat kernels. I'm sure that there's a lot of patterns that basically look like this. Like copying into a buffer and then copying from that buffer into the middle of another buffer, when you could've just copied directly to the middle of another buffer.

##### **Qazalin** [[00:15:29](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=929)]
Also another pattern which is like you want to copy a slice. Or a shrink buffer. Okay. And currently when you want to copy a shrink. It will create a contiguous before the copy.

##### **Geohot** [[00:15:42](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=942)]
Oh I can't believe it still does that. Yeah.

##### **Qazalin** [[00:15:45](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=945)]
Uh, whereas if you have an E_ kernel, the literal E_ kernel that literally just says. That's what I'm going through, at least. But yeah. The good news is that our GEMMs and Flash Attention are pretty much on par with them. And they don't really use any magic kernel, magic fusion that we're not using. We're mostly losing on just having a lot more E_ kernels copying stuff around.

##### **Geohot** [[00:16:12](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=972)]
Right.

##### **Qazalin** [[00:16:14](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=974)]
Yeah. Turns out those are fundamental changes.

##### **Geohot** [[00:16:19](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=979)]
So I'll go through that one.

##### **Geohot** [[00:16:22](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=982)]
Yeah, breakdown with the dichotomy of them is, I think that we are ready to do the fix for the ones that are created in custom kernel and call. All-to-all ones can start to be approached too. I think the cat one we're not ready for yet.

##### **Qazalin** [[00:16:43](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1003)]
Makes sense. I have a little prototype branch somewhere. So I can make a cat kernel. The custom. And it's fast enough. Yeah. Putting that.

##### **Geohot** [[00:16:57](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1017)]
The other thing about the cat kernel too is the cat kernel isn't causing the problem you're talking about with too many kernels. Like the cat kernel may have a bunch of branches and be inefficient, but the cat kernel is still one kernel.

##### **Qazalin** [[00:17:08](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1028)]
Great. The main problem is the many kernels. Three times. Three times. I like that.

##### **Geohot** [[00:17:17](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1037)]
So I'm going to go back to it because we just have a count.

##### **Chenyu** [[00:17:18](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1038)]
We're going to get the count to go down.

##### **Chenyu** [[00:17:26](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1046)]
Can you write a much smaller example that kind of showcases the problem?

##### **Qazalin** [[00:17:37](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1057)]
Yep.

##### **Chenyu** [[00:17:40](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1060)]
Because for the shrink one, I know potential optimization there. That's specifically kind of annoying. I worked on the pad for probably three hours and you'll soon realize there are much deeper problems with that. But I think the all-to-all and copy thing, we should be able to fix it some. So there are so many weird stuff in multi.

##### **Qazalin** [[00:18:16](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1096)]
All right.

##### **Chenyu** [[00:18:18](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1098)]
So yeah, if you have a smaller standalone script that doesn't launch the whole LLaMA run locally or on the MI big machine, that would be very helpful.

##### **Qazalin** [[00:18:33](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1113)]
I'll merge my all-to-all test. That should be comprehensible enough that has everything. Yeah.

##### **Chenyu** [[00:18:42](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1122)]
I know there are at least two odd things in multi. Comment somewhere that some copy is removed later, which is never removed. Something like that.

##### **Qazalin** [[00:18:57](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1137)]
Yeah, there's one bug I found that is funny. It's copying the MSELECT of the thing that already exists on the device. So yeah. Yeah. So it wasn't just being simplified, but then I realized sometimes you don't want to simplify same device copy. Yeah.

##### **Geohot** [[00:19:20](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1160)]
Oh, maybe another way to approach this also is to start with just doing single device. Like how many of these kernels are because of multi, and how many of these kernels are because of some single device thing?

##### **Qazalin** [[00:19:34](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1174)]
Or like model parallel set to one? Yeah.

##### **Chenyu** [[00:19:38](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1178)]
Or I mean, yeah. Yeah. Model parallel one, data parallel one. Just a single GPU.

##### **Qazalin** [[00:19:46](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1186)]
8B fits on a single GPU. I think that's good.

##### **Geohot** [[00:19:50](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1190)]
Yeah. Yeah. That should be easy.

##### **Qazalin** [[00:19:54](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1194)]
OK.

##### **Geohot** [[00:19:57](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1197)]
Well, it sounds good.

##### **Chenyu** [[00:19:58](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1198)]
Let's move on to HCQ2.

##### **Geohot** [[00:20:06](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1206)]
So yeah. I'm not sure.

##### **Nimlgen** [[00:20:09](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1209)]
Dependency tracking, and you can now merge queues. So that's actually the replacement for the graph. I also actually merged the initial implementation of the command-buffer encoding to instructions. That's the intermediate step. But right now instructions have consts as input, and they're not really readable with VIZ, so I'm not sure what I'm going to do about this.

##### **Geohot** [[00:20:54](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1254)]
Where would I see these instructions? So I see that it works on AMD now.

##### **Nimlgen** [[00:20:59](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1259)]
Yeah. Where would I see these instructions? Encode something. Encode cmdbufs, yeah.

##### **Chenyu** [[00:21:10](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1270)]
Oh, I see. Okay, copy ops.

##### **Geohot** [[00:21:12](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1272)]
Yeah. Oh cool. Yeah, in HTML. Yeah, so I see those consts that you're talking about.

##### **Nimlgen** [[00:21:21](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1281)]
Yeah, so actually that's a kind of different flags for the commands, so they're not really readable with VIZ right now. Yeah.

##### **Geohot** [[00:21:36](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1296)]
I also don't see them once I go to the next stage. When I go to lift patches to cmdbuf, I don't see those instructions anymore.

##### **Nimlgen** [[00:21:48](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1308)]
Yeah, because they're merging to binary.

##### **Chenyu** [[00:21:55](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1315)]
Oh, they're merging to binary inside encode cmdbufs.

##### **Geohot** [[00:22:00](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1320)]
yeah

##### **Chenyu** [[00:22:01](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1321)]
got it

##### **Geohot** [[00:22:03](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1323)]
Yeah.

##### **Chenyu** [[00:22:09](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1329)]
Yeah, okay, so there's a bunch of args here and a bunch of like

##### **Geohot** [[00:22:14](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1334)]
inputs. Um, I mean, would the consts be more readable if they were hex? Is that what you're saying, or you want to try to parse them in some better way?

##### **Chenyu** [[00:22:26](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1346)]
I'll try to parse them but

##### **Nimlgen** [[00:22:31](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1351)]
I'll try to do something like that, maybe something in VIZ to better visualize them.

##### **Chenyu** [[00:22:42](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1362)]
I'll try to come up with something.

##### **Nimlgen** [[00:22:53](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1373)]
So, like, this week I'm going to focus on, like, actually we have all the stages we need right now. It works with multi, like the replacement for the graph, because it can merge all these different operations inside one schedule into one longer command buffer and just submit it once. So that's actually the question. When I see `DEBUG=2`, I think I don't want to merge them, just to print the nice statistics. The statistics per kernel. Yeah, so I need to look on this.

##### **Geohot** [[00:23:41](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1421)]
Yeah, I would say that seems right. I would say with `DEBUG=2`, it's kind of the same thing that `WAIT=True` would do. With `DEBUG=2`, I have to wait for the kernel, so they have to launch one at a time.

##### **Chenyu** [[00:23:54](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1434)]
But it seems also that it doesn't work

##### **Geohot** [[00:24:01](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1441)]
for test_mnist. It works for test_plus on my computer.

##### **Nimlgen** [[00:24:07](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1447)]
Yeah, because it's JIT'd, and it doesn't work with JIT yet.

##### **Chenyu** [[00:24:12](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1452)]
It doesn't work with the JIT yet. Okay. I mean, I kind of want it to, like, replace the JIT.

##### **Geohot** [[00:24:26](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1466)]
I see.

##### **Geohot** [[00:24:27](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1467)]
I'm not exactly sure how that's going to work yet, or if you have a plan for what parts of the JIT stay

##### **Chenyu** [[00:24:34](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1474)]
and what parts of the JIT go.

##### **Nimlgen** [[00:24:39](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1479)]
I mean, the only reason why it doesn't work with JIT right now is because JIT has params instead of buffers. And we need a stage to encode these buffer addresses, to write them into a separate CPU buffer and just pass it into the submit C kernels.

##### **Geohot** [[00:24:59](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1499)]
Yeah, got it. Yeah, okay. That's good. So if that's all it's going to take, that's probably just something to put on top of existing JIT. Cool. Yeah, seems like good progress. I think you know the basic direction. Any sort of questions or things that are tricky?

##### **Geohot** [[00:25:19](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1519)]
No.

##### **Qazalin** [[00:25:22](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1522)]
Yeah. Okay.

##### **Geohot** [[00:25:30](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1530)]
That's good. Okay.

##### **Chenyu** [[00:25:32](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1532)]
Next is CI and tests.

##### **Chrism** [[00:25:35](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1535)]
Yeah. So hopefully you've noticed maybe performance improvements in some of the tests. At the very least, certainly the Linux test should be faster.

##### **Geohot** [[00:25:48](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1548)]
Oh, sorry. Is this on? Is this on? Is my audio working? Yeah. Yeah. I can hear you.

##### **Chenyu** [[00:26:02](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1562)]
Okay. Okay. Yeah.

##### **Chrism** [[00:26:04](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1564)]
Okay. Yeah. So hopefully you've seen some improvements there. I need to work on the macOS stuff. The macOS stuff is certainly the slowest. Honestly, I think this is probably the way this is going to work out. Oh, you can't hear me? Or can other people hear me?

##### **Chenyu** [[00:26:25](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1585)]
I can hear you fine. Yeah, I can hear you too. This might be NetSplit. Yeah. Chengyu, you want to try joining or rejoining? Hello?

##### **Geohot** [[00:26:42](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1602)]
Hello?

##### **Chenyu** [[00:26:43](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1603)]
Okay. I can hear you. Can you hear me?

##### **Geohot** [[00:26:45](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1605)]
Yes. Okay.

##### **Chenyu** [[00:26:46](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1606)]
Okay.

##### **Chrism** [[00:26:47](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1607)]
Great. Okay. So yeah, so the macOS tests, probably what this is going to look like is removing a lot of the macOS tests. Primarily, WebGPU on Mac is really slow. So it probably means that we have to slow down a lot of these tests that we do there to get a good performance. Similarly, there's a whole bunch of model tests that are really slow on Metal that probably need to be slowed down. But yeah, that's the general idea. I mean, really, replying to that Docker thing, we can definitely build a big environment that works for everything beforehand and then not have to worry about installing anything to begin with. And then this guy would be happy with that. Although it sounds like he wants something a little bit different. He wants to be able to run NVIDIA stuff through the Docker container with his GPU passed in, which is obviously not what would be running in CI. Oh, yeah.

##### **Geohot** [[00:27:57](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1677)]
I think what he wants is totally different from the CI Docker. Yeah.

##### **Chrism** [[00:28:01](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1681)]
Yeah. But yeah, CI Docker is totally doable.

##### **Geohot** [[00:28:07](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1687)]
Well, yeah. Will it be fast? Like will it load the Docker image quickly?

##### **Chrism** [[00:28:13](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1693)]
Well, I have to test. I'm not totally sure.

##### **Geohot** [[00:28:19](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1699)]
Yeah, I think that's kind of the question. I mean, I'd rather it be like, instead of those bespoke action scripts that install a bunch of things that break all the time, I'd rather it just be like, here's the test Docker.

##### **Chrism** [[00:28:31](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1711)]
Yeah, I think there's a way to do it where it's quick and it doesn't have to build the Docker every time. It just has to download it. And I mean, on namespace, this should be fast. I mean, I can't imagine why it would be slow on GitHub either, but the stuff that's slow on GitHub confuses me and I don't have a good model for why certain things are slow on GitHub and certain things aren't.

##### **Geohot** [[00:28:56](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1736)]
Yeah, I mean, I think it's a question of how large the Docker is. And then like, I mean, it might be kind of annoying. But I think it's a good model. Like, I think it's a good model. for like, you know, like, I don't know, like, I don't know how many gigabytes the CUDA stuff is. Like, I don't know how small we can get the CUDA and the AMD stuff to be.

##### **Chrism** [[00:29:08](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1748)]
The CUDA stuff is actually not that big. Because we're just download, they have like a redistributable where you can just download like specifically the things that you need. So we actually actually CUDA is pretty small. But last I checked, this does not exist for AMD. And you have to basically install everything for AMD for to get any any component to work. So I have to look at that. Well, I think.

##### **Chenyu** [[00:29:31](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1771)]
AMD is simpler.

##### **Chrism** [[00:29:35](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1775)]
I just know that NVIDIA has a website where they release tarballs of like, here's NVRTC. And then you can just download that and that's self-contained and all you need for NVRTC and nvJitLink is in that.

##### **Geohot** [[00:29:47](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1787)]
I'm pretty sure AMD has this too. Okay. It would be great. If we could keep the Docker under a gig, that would be incredible.

##### **Chrism** [[00:29:58](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1798)]
Yeah. We'll see. We'll see. Ocelot also depends on a lot of stuff. Ocelot depends on Boost and some other stuff that I don't totally remember. That's true. Anyway, I have to look into that. It should definitely be doable. I don't know if we can get it under one gig, but it'd be nice if it was.

##### **Geohot** [[00:30:24](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1824)]
Cool. I think also another part of the test project we've been talking about is moving the NVRTC benchmarks to more modern LLMs and maybe splitting some of the benchmarks up. Right now, the comma benchmark is 15 minutes. All the benchmarks should be under five minutes, but it's okay if there's more of them.

##### **Chrism** [[00:30:42](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1842)]
Okay. I can definitely do that. For the LLMs, this probably just looks like the ones that are supported in, it's not apps but `tinygrad.llm` now.

##### **Chenyu** [[00:30:56](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1856)]
We should run those through the Qwen and not the old LLaMA.

##### **Chrism** [[00:31:03](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1863)]
Yeah. Is there any preference for which ones we think are the ones that people care about? I can just choose the plan.

##### **Chenyu** [[00:31:18](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1878)]
Okay. Yeah, that works. Who was I meant to bug about how to get Grafana stuff set up?

##### **Geohot** [[00:31:31](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1891)]
Yeah, I mean, there's the easy set of wins in the test project, which are these things that we should definitely just do. And then there's the hard part of the test project, which is really asking, okay, so what are the factorization boundaries? To answer the question of how many Mac tests we have to run, the deeper question there is, okay, what's different between Linux and Mac? What could possibly break on Mac or on Windows that is different, like a different code path from the Linux? And the same thing is true about backends. So that's...

##### **Chrism** [[00:32:08](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1928)]
Yeah, for sure.

##### **Geohot** [[00:32:09](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1929)]
That's very hard.

##### **Chrism** [[00:32:12](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1932)]
Yeah, I mean, there was some stuff that I felt like, I was like, okay, clearly, we don't need to be testing ONNX on every single backend. But there's some stuff where it's like, okay, this is just not something that we were considering when we factorize the test.

##### **Geohot** [[00:32:27](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1947)]
The way that I would approach this project is to download all the previous test logs and figure out what has failed.

##### **Chrism** [[00:32:34](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1954)]
Yeah, I have done that. I do have all that data.

##### **Geohot** [[00:32:40](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1960)]
But yeah, I mean, focus on the easier wins first. We still have a lot of just mechanical stuff to do.

##### **Chenyu** [[00:32:46](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1966)]
Yeah.

##### **Chenyu** [[00:32:53](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1973)]
So we can update the comma benchmark in smartq. We do have to do that. But yeah, I think it's pretty easy to use their latest release.

##### **Geohot** [[00:33:00](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1980)]
Yes, I will do that. Probably not just the benchmark, but also the test.

##### **Chenyu** [[00:33:09](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=1989)]
Yeah, I think we can just keep a last two version of something. Yeah, yeah, that makes sense. Oh, another thing that's minor annoying.

##### **Chenyu** [[00:33:24](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2004)]
I used to have this cron job that trains ResNet, and ResNet has been broken for a few months.

##### **Chenyu** [[00:33:31](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2011)]
So every day I think it just occupies a machine for half a day. Then I wake up and see that it's running, but I know it will fail. So I kill the job. I should probably just remove that. Yeah, yeah, we should probably just remove that.

##### **Geohot** [[00:33:46](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2026)]
Okay, I will just remove it. Okay. Sounds good. Anything else? I can certainly feel the test is much faster.

##### **Chenyu** [[00:33:57](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2037)]
So that's nice.

##### **Qazalin** [[00:34:01](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2041)]
Great.

##### **Chrism** [[00:34:02](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2042)]
Yeah, I'm glad you, I'm glad you noticed.

##### **Chenyu** [[00:34:04](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2044)]
Comma is, comma, comma benchmark is the only annoying one because if you try to run benchmark from update benchmark, that one will always timeout. Including the process replay, it goes above 20 minutes.

##### **Chrism** [[00:34:18](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2058)]
Gotcha. Okay. Yeah, I.

##### **Chenyu** [[00:34:20](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2060)]
Once we split it, it should be fine. So.

##### **Chrism** [[00:34:23](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2063)]
Yeah, yeah, yeah. Sounds good. I haven't been looking at benchmark.

##### **Geohot** [[00:34:27](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2067)]
Okay. I haven't been looking at benchmarks yet. So I'll.

##### **Qazalin** [[00:34:30](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2070)]
Cool.

##### **Geohot** [[00:34:31](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2071)]
Okay. Next is renderer.

##### **Chenyu** [[00:34:37](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2077)]
So I linked my PR below.

##### **Geohot** [[00:34:42](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2082)]
There was a flag in codegen called new style. I realized that I didn't want to do this as one big refactor with all the renderers at once. We can do the renderers one at a time. New style is like a transformation graph rewrite that goes from what used to be there into some canonical, spec-matching style. Most notably, a few things that are removed are `GEP` is removed, `DEFINE_LOCAL` and `DEFINE_REG` are removed. There's no more casting on pointers. There's no more `dtype.vec`. There's no more dtype pointer. So it follows the spec. It's going to be kind of painful to update all the renderers to the new stuff, but you'll see that everything's passing in that pull request except for the DSP. And the DSP is kind of annoying because in GPU, when you have float4, float4 on a GPU is actually just four registers. They might be contiguous registers, but there's actually four different register IDs. In the DSP, when you have int128, int128 is actually, first off, terribly named because they're 8-bit, so it's char128, and then it's a 1024-bit vector. So there is some distinction between the lanes of a register and the count of a register, and I just need to make sure the story around that is really good to fix the DSP thing. But yeah, there's progress here. It should finally be merged this sprint. What else did I remove? Movement ops are cleaned up. So the only three, well four, movement ops allowed in kernels are `SHRINK`, `INDEX`, `STACK`, and `BITCAST`. And they can do pretty much everything. I mean, `STACK` might be limited to only stack single things. There is some implicit idea that all the kernels are effectively one-dimensional, but they shouldn't even really have to be. It's just nice. So the goal here is, and I should actually test this explicitly, to make sure that all programs we write are also valid tinygrad programs, like all inputs to the renderer can be fed back into the tinygrad optimizer and it all stays within that.

##### **Qazalin** [[00:37:26](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2246)]
Yeah.

##### **Geohot** [[00:37:30](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2250)]
This will remove a whole bunch of ops. And that's what I mean about something that's more important than line count, at least right now, is how many ops do we have? Does every op have a clear definition? Is every op being checked for that definition? Yeah, I did some unification work on `BUFFER` and `PARAM` as well. So `BUFFER` and `PARAM` are the same thing. The only distinction is that `BUFFER` can be rendered, whereas `PARAM` can only be rendered inside of a function. `BUFFER` can be rendered outside of a function. They have the same argument. This argument contains device, address space, min and max, all those kind of things.

##### **Geohot** [[00:38:23](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2303)]
Can't delete `DEFINE_VAR` too?

##### **Chenyu** [[00:38:26](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2306)]
`DEFINE_VAR` should just be `PARAM`.

##### **Qazalin** [[00:38:30](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2310)]
Oh

##### **Geohot** [[00:38:31](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2311)]
Should be what?

##### **Chenyu** [[00:38:33](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2313)]
`DEFINE_VAR` should be `PARAM`. `DEFINE_VAR` is just a parameter shape. Yeah.

##### **Geohot** [[00:38:42](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2322)]
And these things are, I added some machinery to like, so we have this way to encode shapes in UOps. And as a function, your UOp now has shape and it will convert that into a tuple, its shape. I use it in the movement op transformer.

##### **Chenyu** [[00:39:04](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2344)]
Yeah, we use that on a `PARAM` and on `BUFFER`, to make it whatever shape you want.

##### **Chenyu** [[00:39:13](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2353)]
I also saw that you remove Intel and AMX. Yeah. Yeah.

##### **Geohot** [[00:39:22](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2362)]
I mean, they can be added back at some point if we care. I'm sure that Intel thing was broken, and the AMX thing added a lot of code in kind of like the wrong place.

##### **Chenyu** [[00:39:38](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2378)]
Yeah, makes sense

##### **Geohot** [[00:39:40](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2380)]
Yeah, I mean, basically I want everything to follow the spec, and those things do not follow the spec. Those things are like weird hacks.

##### **Geohot** [[00:40:36](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2436)]
Cool. Next is my stuff.

##### **Geohot** [[00:40:42](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2442)]
So mostly work on const, continue on const.

##### **Chenyu** [[00:40:46](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2446)]
I removed the const device. Now we don't have const device. We still have const unique device. That's coming. That's only true for invalid. I'm still studying that. But we don't have other kinds of const device. And I also moved more stuff from tensor.py to mixin. So notably, most of the `__getitem__` and gradients are in mixin now. `__getitem__` will be much cleaner after the removal of `PtrDType`, because the only reason that it's not unified is because we also support special usage of `__getitem__` with `PtrDType`.

##### **Chenyu** [[00:41:43](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2503)]
So now my current focus.

##### **Chenyu** [[00:41:48](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2508)]
So one is unique const and the special requirements in `function.py`. I'm still studying that. The eventual goal is to figure out a way to write an anonymous buffer correctly there. Then the rest of the mixin, I would do the random and its friend there. Random is currently a big block of tensor.py. Then after that, it's a lot of cleaning up for some stuff that involves a little bit of bitcast. So the only reason we have sum, cat, and hash, and I think maybe a few functions, is because we don't have shape-changing bitcast in lower level now. For now, it's a special case that we deal in `Tensor.bitcast`. Once SLICE is done, those can go. And also, I introduced this `_uop` and `_wrap_uop`, because we write a lot of `if isinstance(x, Tensor)`, then access `x.uop`; otherwise, it's `uop`. We have multiple places of that. And so now `_uop` and `_wrap_uop` are just access its UOp, then wrap into its input type. And through this, you can start to look into why tensor is just a very thin wrapper of UOp. And I think that's where the function thing or the metadata will live once all these are done. Basically, when you apply a method to a tensor, it really is accessing the UOp, applying such method, and wrapping it back. And now, I think most of the stuff looks more and more like that style.

##### **Geohot** [[00:44:04](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2644)]
Yeah. I mean, I see that in the mixin on gradient where you're calling `_wrap_uop`. I mean, yeah. Eventually, we don't want tensor to inherit the mixin anymore. We want tensor to dispatch the mixin.

##### **Chenyu** [[00:44:18](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2658)]
Yes. So there are still some annoying things. So for example, for `Tensor.nonzero`, we support the versions that access the item and add those as a parameter thing. It's things like this that we cannot, because we don't want to support item access on UOp, I assume.

##### **Chenyu** [[00:44:49](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2689)]
You want to support what? Do you want to support the item on UOp or the buffer on UOp? I don't think so.

##### **Geohot** [[00:45:03](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2703)]
I think other realization machinery can just be in tensor.

##### **Chenyu** [[00:45:08](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2708)]
So the issue is, you see the current nonzero or anything that requires. These are not JIT-able. And if you try to JIT those, we have an assert. But we allow, we have syntax like this.

##### **Chenyu** [[00:45:28](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2728)]
Yeah. I don't know.

##### **Geohot** [[00:45:29](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2729)]
I think that for things, I wouldn't put them in UOp. I don't think those can live in UOp. I think anything that requires a realization has to stay in tensor.

##### **Chenyu** [[00:45:42](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2742)]
Makes sense. So we can only, for example, for nonzero, we can move the functional part in mixin. But we cannot move the whole thing in mixin.

##### **Geohot** [[00:45:51](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2751)]
Yeah. I mean, nonzero, I think does JAX support these, like can output an arbitrary shape tensor kind of thing?

##### **Chenyu** [[00:45:59](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2759)]
Yeah. At least support both. We match JAX in principle. So the behavior is, if you specify size, that's a fixed output size, then that's JIT-able. And that's functional. And if it's data-dependent, you can also run it. It will give you variable shape output, but you cannot JIT it. So we currently support both like JAX. Yeah, that seems right. Yeah. So that's the current design. And that's kind of where, if it's data-dependent, it won't be part of mixin. And I think that's a fine distinction.

##### **Geohot** [[00:46:40](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2800)]
Yeah, I agree. Is there any reason gradient.py can't move to mixins?

##### **Chenyu** [[00:46:50](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2810)]
Probably no, other than we will create a very big mixin.

##### **Geohot** [[00:46:57](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2817)]
Well. So like right now, I see that inside of mixin init, you have gradient from `tinygrad.gradient` compute_gradient. But I wonder if we could have a gradient mixin that includes all the stuff from `gradient.py`. And then that's just imported and inherited, right? Because the gradient stuff shouldn't require any.

##### **Chenyu** [[00:47:30](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2850)]
I would think about this.

##### **Chenyu** [[00:47:33](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2853)]
Because I think the idea to put in mixin is we will want to write such thing either in tensor or in UOp. But because the gradient machinery is like rewrite engine, we probably want all these functions to be on UOp only.

##### **Geohot** [[00:47:55](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2875)]
Which functions to be in UOp?

##### **Chenyu** [[00:47:58](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2878)]
The existing functions in `gradient.py`. So like full gradient, reduce gradient.

##### **Geohot** [[00:48:07](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2887)]
Yeah, yeah. I mean, they only do take UOps.

##### **Chenyu** [[00:48:10](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2890)]
Yeah, so what's the point of putting those in mixin?

##### **Geohot** [[00:48:14](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2894)]
Oh, it's not really. Just to kind of move the file.

##### **Chenyu** [[00:48:18](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2898)]
You mean moving the `gradient.py` file to the mixin folder?

##### **Geohot** [[00:48:22](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2902)]
Yes, a little bit more than that, though. So right now, I see that gradient is just in op mixin. I wonder if we could have a gradient mixin. It's kind of like it makes the thing differentiable. It has all the machinery you need. Maybe this doesn't actually matter. I just need to move the file.

##### **Chenyu** [[00:48:39](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2919)]
OK, I will start from moving the file and think about it. I think `gradient.py` itself is pretty standalone.

##### **Geohot** [[00:48:49](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2929)]
Yeah, yeah. I mean, what I like about it being in mixin is it's clear that this is some addition on top of the UOps. Nothing downstream of mixins should have anything, should need any knowledge of these things. Unfortunately, right now, this isn't true for multi, for example.

##### **Chenyu** [[00:49:12](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2952)]
Multi introduces crap like `MSELECT` and `MSTACK`. But gradient shouldn't introduce anything like that.

##### **Geohot** [[00:49:23](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2963)]
Gradient should be pure mixin.

##### **Chenyu** [[00:49:25](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2965)]
Mm-hmm.

##### **Chenyu** [[00:49:27](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2967)]
Yep, that's all good.

##### **Chenyu** [[00:49:29](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2969)]
OK, I'll move this and see what update I would do on this.

##### **Chenyu** [[00:49:40](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2980)]
That's pretty much it.

##### **Geohot** [[00:49:45](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2985)]
OK, move on to issues.

##### **Chenyu** [[00:49:51](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2991)]
This issue is Comma happiness. Is Comma happy? I don't think they support tinygrad.

##### **Chrism** [[00:49:57](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=2997)]
Yeah. They're using your, I think it's like a PR title, like image hack for #16335, which I believe means that if they want to bump, then they're going to have to rebase that tinygrad.

##### **Chenyu** [[00:50:16](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3016)]
Or maybe they can contribute a fix, a fix for it.

##### **Chrism** [[00:50:21](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3021)]
I can see if there's any interest in that. But my guess is that there's probably not going to be very much interest.

##### **Chenyu** [[00:50:27](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3027)]
I mean, I don't mind rebasing. I just don't want to maintain a hack. I really hope that's just temporary. But someone needs to fix that.

##### **Qazalin** [[00:50:37](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3037)]
Yeah.

##### **Chenyu** [[00:50:39](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3039)]
Yeah, yeah, yeah, yeah, yeah. I don't know.

##### **Geohot** [[00:50:45](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3045)]
I don't understand that hack. I looked at it. It looks like some unreadable GPT slop.

##### **Chenyu** [[00:50:52](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3052)]
Yeah, of course.

##### **Geohot** [[00:50:54](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3054)]
Yeah, I think we talked about this last week. But yeah.

##### **Chenyu** [[00:50:57](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3057)]
And I think probably has the same access to the same GPT as I do.

##### **Geohot** [[00:51:03](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3063)]
Can we get a simpler repro that's not like an ONNX runner?

##### **Chenyu** [[00:51:10](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3070)]
No, not really. I think a lot of it is.

##### **Chenyu** [[00:51:13](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3073)]
I tried to have a scaled-down version of that. It's just it really needs to be a complicated construction to trigger the rangeify path. Yeah.

##### **Qazalin** [[00:51:31](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3091)]
Yeah. Yeah. Yeah.

##### **Chrism** [[00:51:39](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3099)]
So I'll also have to double check if they're even hitting this path still. Because I got pinged in an issue where they tried to bump. And they had an arange with device set, and you can't do that anymore. But if they're trying to bump tinygrad, then anyway, I don't know. So I will ask and see if maybe they don't need this fix anymore, but I don't know.

##### **Chenyu** [[00:52:05](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3125)]
Yeah. OK, this time we cannot ask them to file an issue, because they did file an issue. Oh, no. Let me know if there is a new requirement, or maybe you can just reply to that issue, and I will take a look to see what to do with this hack.

##### **Chrism** [[00:52:25](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3145)]
Yes, I will bug them and see exactly what's going on with that, because I'm a little unclear. And then the other thing is that they're trying to ship this big transformer, and they were wondering about Flash Attention

##### **Geohot** [[00:52:40](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3160)]
support on the 9060. Yeah, I mean, it should.

##### **Chenyu** [[00:52:51](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3171)]
They could use the AMD Flash Attention. It's pretty good. Does that work on 9060?

##### **Geohot** [[00:53:00](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3180)]
It should.

##### **Chenyu** [[00:53:02](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3182)]
OK. But is that accessible from ONNX?

##### **Chrism** [[00:53:07](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3187)]
Or is it like? No. Yeah.

##### **Chenyu** [[00:53:10](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3190)]
It's an extra.

##### **Chrism** [[00:53:12](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3192)]
Yeah.

##### **Chenyu** [[00:53:13](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3193)]
They can copy that thing. OK. OK, I think the other one should have an issue,

##### **Chenyu** [[00:53:22](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3202)]
or at least come up with a, you cannot come to us and say, we want Flash Attention. You should say, we are trying to run this, but it's too slow. So.

##### **Chrism** [[00:53:33](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3213)]
That's kind of what I said.

##### **Chenyu** [[00:53:35](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3215)]
OK.

##### **Geohot** [[00:53:38](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3218)]
But I also promised that I would bring it up. So I brought it up.

##### **Qazalin** [[00:53:47](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3227)]
OK.

##### **Geohot** [[00:53:49](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3229)]
I don't know. PR. PR.

##### **Qazalin** [[00:53:56](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3236)]
PR. PR. PR. PR.

##### **Geohot** [[00:54:06](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3246)]
I see these two NV PRs. There's one NV PR with the copy that's replaced by something really slow and this disable bus mastering. They're kind of AI, but they kind of do something we want. And then, Nimlgen, I see you replied to one of them, or both of them.

##### **Geohot** [[00:54:30](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3270)]
So I think we should just go ahead and do it. I think we want them, but maybe not the way they implemented.

##### **Chenyu** [[00:54:40](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3280)]
Yeah. I mean, if we want them to change it,

##### **Geohot** [[00:54:42](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3282)]
you've got to give them feedback to change it. Or maybe it's just quicker for you to do it if you want them. OK. And issues.

##### **Chenyu** [[00:54:59](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3299)]
I mean, there are a bunch of external GPUs that we just close, ignore, or something. Oh, this is a real, real regression. There's this random seed reuse bug. The post in the schedule channel, it's real. It's after we do the preallocate all the buffers and change to this code style, there are some ordering things that we didn't test. And it's real.

##### **Chenyu** [[00:55:31](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3331)]
That's pretty bad, yeah. Yeah.

##### **Chenyu** [[00:55:34](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3334)]
I'd probably spend another half day on this. I don't have a good solution.

##### **Geohot** [[00:55:40](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3340)]
I marked it as real issue.

##### **Chenyu** [[00:55:43](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3343)]
So the problem is all our interdependencies concern a single schedule or a single realize. And we don't merge other tensors just because it's a dependency. Something like that. But it's pretty bad.

##### **Chenyu** [[00:56:08](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3368)]
Yeah. I see what's happening. I see why that happens. Yeah.

##### **Chenyu** [[00:56:14](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3374)]
Yeah.

##### **Chenyu** [[00:56:15](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3375)]
I don't know. It's a real issue.

##### **Geohot** [[00:56:19](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3379)]
OK. So there's that.

##### **Chenyu** [[00:56:24](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3384)]
What else? Oh, Flata also complained something. You want to say something?

##### **Flata** [[00:56:30](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3390)]
Yeah. I thought that `buffer=False` location caused the issue. But I added some gradient checkpointing for mine. And I split the train step to be doing the optim step in a different function, just similar to LLaMA. And that pretty much fixed most of the out-of-memory issues that I was having.

##### **Chenyu** [[00:56:54](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3414)]
OK. So you hit a regression? Or is it a bug? Or just script needs to be updated?

##### **Flata** [[00:57:03](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3423)]
That's a good question. I think it's more, I don't know if I really hit a bug. Or I think it's more of a regression, possibly. But I can't really confirm now because there are a lot of variables. But hopefully I can investigate it further and give a definitive answer.

##### **Qazalin** [[00:57:20](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3440)]
Yeah.

##### **Flata** [[00:57:21](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3441)]
That's fine.

##### **Chenyu** [[00:57:23](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3443)]
Because I know the update to the arange and const might potentially need upgrades to downstream code. It's a real API change, kind of.

##### **Flata** [[00:57:36](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3456)]
Yeah, it was very subtle.

##### **Chenyu** [[00:57:38](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3458)]
So it's definitely hard to detect at first. What does that look like? Does it work? Does it train?

##### **Flata** [[00:57:49](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3469)]
Yeah, it looks like it is training. I just want to just verify. But yeah, it does look good so far. I'm just running like 10 steps, something very small

##### **Chenyu** [[00:57:56](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3476)]
at the moment.

##### **Geohot** [[00:58:06](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3486)]
Good. Okay. Anything else for the meeting? Any last words? Oh, I think everyone kind of knows what they're doing. Great.

##### **Chenyu** [[00:58:27](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3507)]
Great. That's good. Okay, that's it for this meeting. Thank you everyone. See you next week. Bye. Bye.

##### **Chenyu** [[00:58:35](https://www.youtube.com/watch?v=8Lfha_DNm7A&t=3515)]
Bye.
