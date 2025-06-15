# 2025-06-02 Meeting

> Note: This transcript was generated in one shot without review. There may be errors, inconsistencies, or inaccuracies in the transcription.

### Meeting Agenda

**Time:** 9am Monday San Diego time
- company update
- mlperf, benchmark ci jobs
- more about ci stability
- scheduler, qcom?
- drivers
- cloud hashing stuff
- onnx
- local
- webgpu
- symbolic z3 stuff
- other bounties (lm_eval, AMD_LLVM, cloud)

### Audio

[Youtube Link](https://www.youtube.com/watch?v=xyn3mZGiXd8)

### Highlights

- **[Company Update](#geohot-000111)**: Tiny boxes are shipping; positive discussions ongoing with AMD to improve MLPerf results.
- **[MLPerf Benchmarks](#chenyu-000132)**: Official MLPerf results releasing Wednesday; daily cron jobs running ResNet and Stable Diffusion XL with varied reliability; focusing on CI stability.
- **[CI Stability](#chenyu-000315)**: CI experiencing frequent benchmark failures; ongoing issues with AMD driver memory errors and instability; prioritizing AMD LLVM integration to improve reliability.
- **[Scheduler and Qualcomm](#qazalin-000610)**: Fusion refactoring nearly complete; addressing regression in OpenPilot; no new updates on Qualcomm.
- **[Driver Stability (AMD)](#nimlgen-000814)**: Kernel page faults linked to AM drivers; issues likely related to queue memory locations; testing memory queue changes as potential fixes.
- **[NVIDIA Issues](#nimlgen-001425)**: Investigating kernel issues on 5090 GPUs reported by users; request for detailed logs to aid debugging.
- **[Cloud Hashing & Local Compile](#wozeparrot-001718)**: Progress on hashing projects; discussing PR to handle remote compilation locally; considering architecture changes to allow explicit local compiler specification.
- **[ONNX Integration](#chenyu-002240)**: Qualcomm-specific bugs blocking ONNX protobuf PR; plans to enhance ONNX support and automated testing once resolved.
- **[Visualization & Layout Tools](#ignaciosica-002521)**: Developing layout visualization tools; standalone scripts proving helpful for debugging tensor layouts and padding issues.
- **[WebGPU JIT Refactor](#hooved-002836)**: Proposed refactoring for JIT captures; detailed discussion required on implicit input/output behavior and realization handling; flags discouraged—need further documentation and testing before merging.
- **[Symbolic Z3 and Bounties](#sied-lykles-005401)**: Symbolic fuzzer merged; work needed on individual rewrite rule tests; other bounties progressing, notably AMD LLVM integration nearing completion.
- **[General Project Note](#geohot-005810)**: Reminder for higher-quality PR submissions; caution against using AI-generated low-quality code.

### Transcript

##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=0)]
Let's get started.
Company update.
I don't have anything to update.
Woze do you know anything about Tinybox?
I also don't know if Woze is there.

##### **Chenyu** [[00:00:26](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=26)]
Let's skip the company update unless any of you
insiders have any more info, my understanding is we are shipping boxes, and we got more orders of new boxes.
So that should be good.
And I am flying to San Diego later this week.
We'll have in-person sessions to discuss Tinycorp and Tinygrad stuff.

##### **Chenyu** [[00:00:57](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=57)]
And moving on to
Hello?
Can you hear me?
Yes.
Did you say something?

##### **Geohot** [[00:01:11](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=71)]
Oh, yeah, no, just about the tiny boxes.
They're shipping.
Things are good.
And I had a few good email exchanges with AMD last week.
So yeah, there's a chance we're going to
Be really working to drive those MLPerf scores down.

##### **Chenyu** [[00:01:32](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=92)]
Great.
Good to know.
Speaking of MLPerf, so official result is out this Wednesday, I believe, like Wednesday US time.
Yeah, I think AMD.
Since they made a submission and they are really looking to drive the numbers down, we will see more about those results with the official announcement.
Our time is May, so there's that.
And I have moved the... So there are two benchmark jobs running about MLPerf.
One is ResNet running on Red Machine.
And I also have another job that runs the stable diffusion XL.
The ResNet job is running daily every day now.
And so far it's a mix of, I think the successful rate is like 30%.
And we will talk more in the next point.
I want to discuss about the stability of our CI now.
And the other one I really want to also make a cron job is the stable diffusion XL one.
For some reason, the GitHub action is constantly slower than if I just run the job on the real machine, and I really don't know why.

##### **Chenyu** [[00:03:07](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=187)]
After, oh, I mean, I can post what I have now, but I don't have other.

##### **Chenyu** [[00:03:15](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=195)]
Attempts to make it comparable.
I really want to make it comparable.
Otherwise, it's really hard to track as a periodic cron job.
I will also add the CIFAR to the last thing.
For now, I think it takes about 20 minutes to run.
We can still start with a daily cron job.
And the CIFAR thing, I think, is also similar.
It should be good.
But speaking of the CI stability, if you go to Tinygrad GitHub page and check the CI history, you will see a bunch of benchmark are failing.
So I think one is the green machines.
One green machine is weird and consistently go out of memory.
And there are all sorts of issues with red machines that I just complained in the AMD channel.
I still believe there are latent issues with AM drivers.
Maybe we can talk more when we move on to the driver section.
But I think we discussed about a lot of driving Tinygrad adoptions.
I think ML training is one thing.
Using our drivers is another.
Our goal is to make these neural nets run and run smoothly on all hardware.
I got frustrated running these on our setup, and I already am probably one of the power users already.
And if I feel bad, I feel it's probably worse for our user.
So I feel for the Tinygrad adoption and driving more users to use it is important to make it more stable.
And to that front, we will talk about more, but I think we are good to
Using AMD LLVM or basically bring all the complexity and issues with bugs to our own stack.
So I was trying pretty hard to make AMD LLVM default.
And from there, we should be able to fix and make it more usable.
Otherwise, it's really frustrating to make it work.
So we should strive to make our CI better, and we shouldn't let it stay red for too long.
Otherwise, people just ignore it, and it's become annoying to develop on top of that.
OK, that was my rant, and we can move on.
I didn't do much development-wise last week.
I fixed a bug with the parentheses.
There might be more to that, but that was my main thing.
With that, we can move on to scheduler.

##### **Qazalin & Chenyu** [[00:06:10](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=370)]
Yeah, on my end, I'm working on moving all the Fusion stuff
Basically, reordering the G-barriers.
There is a final regression in OpenPilot.
I need to investigate.
I'm happy about that.
Chenyu: You are being cut.I cannot quite hear you.
Is it good now?
Chenyu: Yes, maybe.
Chenyu: I heard something about open pilot regression is the last thing.
Chenyu: It is the last blocker, yeah.
I'm just going to move a bunch of stuff.
Chenyu: The blocker for enabling what?
Just refactoring Fusion.
The thing that decides which intermediates to realize is this custom thing that has existed as long as the scheduler was a concept.
So it's the oldest part of the scheduler that I need to rip out and make it modern.
Chenyu: Ok,Sounds good.
Chenyu: And I was not sure, but I guess nothing new for the Qualcomm.
No.
Chenyu: Okay.Okay, no problem.
Let's move on to driver.

##### **Nimlgen** [[00:08:14](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=494)]
Yeah, so I suppose, yes, stability, I think.
Yeah.
You reported several bugs about llama and like
So, actually, I mean, the page faults are, actually, I mean, like, for the half of the year, we've never seen page faults in AM related to AM.
So, I think that the page faults which are reported as page faults are
Kernel page faults.
And we had some tooling to repro these kernels, like beamed kernels in heap or AMD, but it was ripped off.

##### **Chenyu** [[00:09:09](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=549)]
Yeah, so I think in terms of usability, I'm fine trying all these stuff.
And I mean, if reporting these as a specific issue helps you try out the issue, I'm happy to do that.
For me, it's more of a, I have seen three, four different kinds of failures.
And other than retrying stuff, I have no way to really understand what's happening.
And that makes it pretty hard.
So I don't know if you have any suggestions.
Maybe an issue template would help, something like that.
Things I can try or things I can let you know to reproduce or anything that would help.

##### **Nimlgen** [[00:09:55](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=595)]
Yeah, I can think about that.
Generally, I mean,
Yeah, okay, yeah, I'll think about that.
So, and the issue, I think, with NAN issues in BERT we had, and this ResNet issue today.
So, yeah, I think it looks like they are really like AM related, and it might be the, like, we have two differences in AM comparing to the AMD driver.
Uh, first is like the, that we just ripped off the mess.
And the second one is like the location of our queues, because I mean, we use queues.
We shall store it on like queues, uh, on AM is stored on the device and AMD stores them in system memory.
So that's actually the different because they, it's just completely different path with
Interrupts and so on.
I mean, in our case.
So that might be the issue with some sync issues we see.
Yeah, and we need to test that and maybe match AMD here.

##### **Chenyu** [[00:11:16](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=676)]
Yeah, I think this should be a priority because value error is kind of very hard to detect.
I mean, sure here we are lucky because if it's NAN during training, or if it's like completely garbage value, it's very easy to tell, but it's also likely like this can be silent and something just slightly go wrong.
And that's really bad because it's very hard for user to tell.

##### **Nimlgen** [[00:11:46](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=706)]
Yeah, but actually like from, yeah, I've seen these issues only in the training and I just tried to reproduce them.
Like in the all-reduce thing, like just sending data between GPUs.
And I've never seen that.
So yeah, I mean, that's .

##### **Chenyu** [[00:12:04](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=724)]
So for now, it seems to be something like, both for BERT and for ResNet, it seems to be something that only happens after a few hours of running.
So that's even worse, because it's even harder to reproduce.
But then I still think it's important, and we should find a way to figure it out.

##### **Nimlgen** [[00:12:25](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=745)]
Yeah, and I think that's the AM issue and not the graph issue because I'veseen some crashes like on the second step and it's not jitted.
So yeah, it should be some sync issue here.
Yeah, I'll try to, yeah, I'll switch to, I'll switch queues to system memory and we'll see if it's better.

##### **Chenyu** [[00:12:53](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=773)]
Yeah, I mean, if you have candidate fix, we can definitely enable those on our CI job to see if it's better.
Because this is kind of a subtle fix.
So maybe our best strategy is to enable that on the Cron job.
And it's probably fine to make it
Since we have one more machine now, I think it's fine to make it run maybe twice a day or something and see if the fix is more stable.
Maybe that's the best we can do.
Definitely want to prioritize some kind of fix and test it, since fixing this takes a long time.
Not necessarily a lot of developing time, but just because we need to run maybe dozens of runs to know if it's truly fixed.

##### **Chenyu** [[00:13:48](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=828)]
Yeah, cool.

##### **Nimlgen** [[00:13:51](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=831)]
Yeah, so for NVIDIA, I got some RPC messages.
So yes, I'm talking with the Falcon CPU.
So yeah, it's still not done.
I mean, all this virtual memory, and yeah, it's a to-do.
I'll do this, this week.

##### **Nimlgen** [[00:14:25](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=865)]
Actually, Woze you said that you've seen some problems around ResNet on 5090s.
I don't know.
I just tried to repro this on the single 5090.
Like with Beam and just, it was fine.
So if you have any details, it would be good to know.

##### **Chenyu** [[00:14:50](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=890)]
Oh, I didn't test on 5090.
Was that from George?

##### **Nimlgen & Wozeparrot** [[00:14:55](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=895)]
Nimlgen: No, Woze said that.
Woze: That was from me.
Unfortunately, I don't know if I have logs for it.
It was on the machine.
It was on that Tinybox V2 that was going out to people that don't have logs on this.
If I ever reproduce it on another one, I can send you logs.

##### **Nimlgen** [[00:15:23](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=923)]
Yeah, it would be great.
Actually, I mean, there should be some problematic kernel like we hit during Beam.

##### **Wozeparrot & Chenyu** [[00:15:32](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=932)]
Yeah, I'm assuming it's that.
Chenyu: OK.
Chenyu: I think we can try it.

##### **Chenyu** [[00:15:42](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=942)]
I think maybe we should start to create more concrete issues for these.
So we have something to track and something to make sure we are improving on this front.
By the way, so what's the, do we run anything MLPerf for the new TinyBox v2 before we ship?

##### **Wozeparrot** [[00:16:07](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=967)]
It's the same as Tinybox v1.
We still do a ResNet training run, the same provisioning stack.

##### **Chenyu** [[00:16:14](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=974)]
I assume it doesn't.
But it's 4 GPUs now.
So did you change batch size or something?

##### **Wozeparrot** [[00:16:22](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=982)]
No.
It's mostly same settings.
Chenyu: With 4 GPUs?
Wozeparrot: Yeah.
Chenyu: How do you do that?

##### **Chenyu** [[00:16:30](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=990)]
Same batch size?
I mean, it's probably divided by 4, but OK.

##### **Chenyu, Wozeparrot & Nimlgen** [[00:16:33](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=993)]
Wozeparrot: Yeah, it just divides by 4.
Chenyu: OK, great.Cool.
Anything else for driver?
Nimlgen: No.
Chenyu: OK.
Chenyu: OK, moving to Wozeparrot your stuff.
Wozeparrot: I think [lepot](https://github.com/tinygrad/tinygrad/pull/7186) is doing pretty good for hashing.
Chenyu: Did you merge that?
Wozeparrot: Making decent progress. So I think we're just we'll be good on that.
Then I have a PR open.

##### **Wozeparrot** [[00:17:18](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1038)]
I don't know how exactly we want to do this the current way that I have a PR open for doing remote compile locally.

##### **Wozeparrot** [[00:17:28](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1048)]
It's a little jank.
And then
Not entirely sure how we want to do this because the current way is I'm fetching the compiler just from the remote target.

##### **Wozeparrot** [[00:17:43](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1063)]
But that means that you can't switch which compiler you're using on your host machine.

##### **Wozeparrot & Chenyu** [[00:17:52](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1072)]
Wozeparrot: Does that make sense?
Chenyu: Not really.

##### **Chenyu** [[00:17:57](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1077)]
Can you describe how this is supposed to be used?

##### **Wozeparrot** [[00:18:02](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1082)]
You set local compile equals one and then you'll compile all the kernels locally rather than on the remote machine.

##### **Wozeparrot** [[00:18:11](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1091)]
The main problem with the way it's currently set up is if you set, you have to set flags like AMD LLVM equals one on the remote rather than on your host, even though the compiler option should be a host option.

##### **Chenyu** [[00:18:30](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1110)]
That's weird.
Okay.

##### **Chenyu & Wozeparrot** [[00:18:34](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1114)]
Chenyu: So I guess the final goal is we have a local compile or maybe an instance that's specifically used for a compile.
Chenyu: Then after a compile, it sends the exact item to remote, and it runs on remote?
Wozeparrot: Yeah.Yeah.
Chenyu: Ok. And so what makes this PR janky?

##### **Wozeparrot & Chenyu** [[00:18:59](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1139)]
Wozeparrot: Mainly just the thing where it fetches the compiler from the remote.
Chenyu: Oh, because you don't really want or need the compilers from remote.
Chenyu: You want the compiler on host.
Wozeparrot: Yes.
Chenyu: I don't know. So maybe it's fine.

##### **Chenyu** [[00:19:24](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1164)]
This sounds like something I can use a document or something to say what we want to do.

##### **Wozeparrot** [[00:19:33](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1173)]
Yeah.

##### **Chenyu** [[00:19:36](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1176)]
Because I don't know if there are alternative considerations here, right?

##### **Wozeparrot** [[00:19:42](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1182)]
Yeah.

##### **Chenyu** [[00:19:44](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1184)]
If you don't ever really need a compiler on remote, then I don't see this as, this cannot be the only way to do it, right?
You have compilers run your host, you will use that.
Maybe you have more explicitly specific, you can specify like which compiler you use, something like that.
I don't really know.

##### **Wozeparrot & Chenyu** [[00:20:07](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1207)]
Wozeparrot: That's the main problem with this is that you can't specify which compiler you use on your host.
Wozeparrot: Because it always fetches it from the remote.
Chenyu: I don't know.That sounds something like, how do you do multiple remote?
Wozeparrot: Yeah, that's the other thing.
Chenyu: OK. I really do listen to that.

##### **Wozeparrot** [[00:20:33](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1233)]
Wozeparrot: This feels fine multi-GPU and remote.Uuuvn has pretty good stuff on that.
Chenyu: Yeah, but that's one remote there.
Chenyu: Yeah, I feel this can use at least a little bit of write-up to say what was considered before we know if this is good or bad.
Chenyu: Because just by the way you describe it, it doesn't sound like the best design.
Wozeparrot: Yeah
Chenyu: But if you tell me this is the easiest way, I don't know.I think this can use a little bit of write-up.
Wozeparrot: OK.
Chenyu: OK, let's write a little bit of this and maybe just I don't I don't know what you intend to run after this is done.
Chenyu: Do we have like some testing stuff?

##### **Chenyu & Wozeparrot** [[00:21:28](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1288)]
Chenyu: Things you want to test?
Wozeparrot: Yeah.Not entirely sure yet.
Wozeparrot: We have some remote tests in CI.
Wozeparrot: Could I just start off with that?

##### **Chenyu** [[00:21:45](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1305)]
I don't know if this is related.
I'll figure it out later this week.
But I really want to look into running llamas inference.
So we should be able to have, like, taking their model maybe in ONNX form and run something like a remote.
I don't really know.
But I want to.
For one part drive adoption of Tinygrad, we definitely did that for [Comma's](comma.ai) on-device inference.
And the next step is probably their model roll-up and stuff.
So that's something I'll really look into.

##### **Chenyu & Wozeparrot** [[00:22:26](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1346)]
Chenyu: Maybe that's related to the remote setup and what we can use.
Wozeparrot: Yeah.
Chenyu: Oh, great, since we talk about

##### **Chenyu** [[00:22:40](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1360)]
Running Comma's ONNX model, we can move on to ONNX.
So ONNX I think has two parts.
The first is the ONNX protobuf thing.
See B1TG is here.
I think the blocker for that is Qualcomm.
And I really don't know what's happening to Qualcomm.
I also don't know if you have access to any of the Qualcomm.
If not, I can add you to one and maybe you can look.
It looks like a value is wrong, and that's the worst kind of bug.

##### **B1tg** [[00:23:15](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1395)]
Yes, I didn't reproduce it with a VM or GPU backend, so maybe I can get access to a machine with Qualcomm so I can debug that.

##### **Chenyu** [[00:23:33](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1413)]
After the meeting, I will make sure you have access to a Qualcomm machine.
I think once that is resolved, we should be able to merge that PR.
And I believe that will greatly simplify the moving ONNX to Tinygrad proper.

##### **Chenyu** [[00:23:53](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1433)]
I think that's it.
Zibokapi, do you have anything to add to that?

##### **Chenyu** [[00:24:11](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1451)]
OK, yeah, so I think that's another part that we want to focus like soonish.
Using ONNX as a front end, importing ONNX, running the model should be straightforward.
And similar in that spirit, we add the protobuf parser.
We implement the ONNX ops.
Things like that hopefully should move more after we have done these two parts.
And we should try to really run those ONNX CI tests running various different models, trying to make sure they're all run correctly.
OK, here Uuuvn said something, something will be done soonish.

##### **Chenyu** [[00:25:13](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1513)]
With that, I'll move on to local.

##### **Ignaciosica** [[00:25:21](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1521)]
Last week, I've been working on the layout visualization.
I think it will be, I will have a draft for today, for later today.
Regarding locals, I fixed the problems that the change in the API for the view, the store load view buffer.
So that's fixed.
So the state of the PR, it's basically the same as it's been for the past weeks.
The only thing that's blocking it right now, I think it's that it doesn't work with padding.
And I think there's no reason why it should be.
And that's why I started to work on the viz for the layout, because it might help me figure out what's going on.
So yeah.

##### **Ignaciosica & Chenyu** [[00:26:13](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1573)]
Ignaciosica: That's progress.
Chenyu: PADDING is wrong.

##### **Chenyu** [[00:26:22](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1582)]
So I saw you post a pretty good looking graph in the Viz channel.
Do you intend to as well?

##### **Ignaciosica** [[00:26:30](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1590)]
Yeah, that's what the draft PR I was talking to I was going to do later today.
The thing about this is that for some cases, it's not
I don't feel comfortable.
I didn't feel comfortable yet.
Because if you have a visualization of something, you want that to be reliable.
Because if that visualization is wrong, it's even worse.
So I've been testing in some edge cases that it's correct.
So that's it.

##### **Chenyu** [[00:27:07](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1627)]
I think the idea is we want these tools if it helps you during development.
I think being able to see the tile and being able to see the layouts definitely help with Tensor core stuff.
So I think the idea is if it helps you, then find a way to make it maybe even a standalone script or something, like being able to generate graph
Graphics like this is already pretty helpful in some cases.
But even if it's not fully upstream, I think this would be a benefit.

##### **Ignaciosica** [[00:27:44](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1664)]
Yeah, I think you're right.
I think it will work way better as a standalone script.
I was trying to catch every case for it to be upstream in kernel.py, but I think it will work.
Way better as a standalone script.
This is useful in some cases already.
So yeah, I think it is.

##### **Chenyu** [[00:28:08](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1688)]
It's like low tensor core swizzling.
If there's an easy way to print it as a script, I think it will already be helpful.

##### **Ignaciosica** [[00:28:19](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1699)]
Yeah, yeah.

##### **Chenyu** [[00:28:21](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1701)]
Ignaciosica: Great.Thank you.
Chenyu: It looks pretty nice.
Chenyu: Okay, moving on to WebGPU.

##### **Hooved** [[00:28:36](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1716)]
So I have a new PR open that's ready for review on refactored JIT capture.
And there's a short write up in there and how it works.
But basically, after the meeting last week where we discussed some of the edge cases involving explicit and implicit inputs and outputs,
I realized that what I had been doing a week ago is just not sufficient, so I took a new approach where we ban all realizes within the function we're capturing or within the JIT function we're capturing unconditionally.
Last week, there was this thing there about certain UOPs, but that's gone.
It's very simple, just no realizes.
So just one single line added to tensor.py.
And so the new strategy is we're able to
Figure out what to capture, covering everything just by knowing what the tensor graphs looked like before and after we call the function.
And with that information, it's actually pretty concise to deduce what happened.
And you can capture all that.
And in addition, it's very powerful to know
What the tensor graphs looked like before you called the function, because that also solves some other problems that I've been struggling with.
One of which is, since you know what history looked like before you called the function, you can realize, well, first of all, that just tells you right off the bat what the implicit inputs are.
It's a pretty simple definition.
And second of all, it lets you realize those if they haven't been realized.
Which is mandatory to have the data in the right place to export it for web GPU and other stuff.
And then third of all, after you've called the function that you're capturing,
That leaves lazy computation on the implicit inputs or outputs, on the outputs or the inputs if they're mutated.
And since you know what those look like before you call the function, you're able to effectively rewind that lazy computation and not leave it in user space.
So it is looking at global state, but it's very powerful to do so.
And there's a couple of weird edge cases where if you mutate implicit inputs, they go into different buffers.
So that's like the only thing that just feels kind of ugly but has to be dealt with.
And yeah, so that's ready for review.
And everything else in the WebGPU refactor basically is just about ready.
But it all depends on this.

##### **Chenyu** [[00:31:40](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1900)]
So yeah, I'm reading this PR.
Is there a reason why ban realized it's not a default behavior?

##### **Chenyu** [[00:31:53](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1913)]
Yeah.
Well, so yeah.

##### **Hooved** [[00:32:05](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1925)]
If you look at the test cases, it shows you in the test where you need realizes in some of the cases, where you need them to happen.

##### **Chenyu** [[00:32:15](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1935)]
My point is, is it preferable to make ban realize the only behavior by not introducing this?
And if the only place is that this fail is in some test case, we can just update the test case.
Because it's really annoying to have a flag like this and allow both behavior, right?

##### **Hooved** [[00:32:43](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1963)]
Oh, so I think maybe I see what you're saying.
Why do we have this whole new thing with the flag?

##### **Chenyu** [[00:32:49](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1969)]
Basically, why is ban realize a flag?
And every time we introduce a flag, we need to think about what's the default value of a flag?
What happens if the user changes the flag?

##### **Chenyu** [[00:33:06](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1986)]
I think unless there's a strong reason why we still want... The case where you need to realize?
Say that again?

##### **Geohot** [[00:33:12](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=1992)]
I see the reason why... So the problem is if you do an assign inside of a JIT, if you don't realize that assign, it may not end up in the JIT.
So I'm not sure exactly how we want to deal with this, but yeah, no, I don't think ban realize should be a flag.

##### **Chenyu** [[00:33:36](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=2016)]
Okay.
So like what you Okay, go ahead.

##### **Geohot** [[00:33:42](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=2022)]
I mean, what you can instead do instead of actually, it definitely shouldn't be an environment variable, right?
What you can instead do is you can just check for JIT v2, if any realizes happen, and then just throw a runtime error there.

##### **Chenyu** [[00:33:59](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=2039)]
Sure.

##### **Hooved** [[00:34:00](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=2040)]
I mean, that's easy.
Sorry, I think I better understand.
You just don't like the flag.
So yeah, we could get rid of that.

##### **Chenyu** [[00:34:09](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=2049)]
Yeah, because so flag is only if we want both behaviors, right?
Because having flag just exponentially increases your things you need to test and you need to consider.
So, I mean, yeah, assign seems to be a reasonable case.
We definitely have those in our examples.
It shouldn't be a flag and should be dealt like differently.

##### **Hooved** [[00:34:47](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=2087)]
I guess in my mind, trying to finish this stuff I've been working on, I just want to get feedback.
I guess part of the issue is this is a completely different way of doing the JIT than what we're currently doing.
And I understand it's like a refactor.
Part of the issue is that it's a new thing, and it's not thoroughly tested.
But I was sort of doing it because that's the direction we wanted to go in, having everything be computed ahead of time without running stuff, which is different than the current JIT.
And is the current approach sound, and can we
We can figure out the flags, but can we just move forward with it so we can merge the rest of the web GPU stuff?

##### **Geohot** [[00:35:46](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=2146)]
So yeah, I don't think this is the way to, like, this idea of, OK, we just need to get a flag merge so we can get something else merged, this never works.
So I wrote that test with the test JIT cases.
We have to think through what we want the behavior to be.
So what do you do fundamentally if you're doing an assign inside of a JIT?
How do you get that to trigger inside of the JIT?
Should that be allowed?
Should that have to be returned?
That needs to be thought about conceptually before we put that into code.
And the truth is, I don't have an immediate answer.
But you can see the case.
The case is just if you have an assign and that assign is otherwise disconnected from the graph.
If that assign is connected to the graph, it's going to realize when you realize the final JIT.
But if it's not, well, then those realize.
So what behavior do you want?
You have to understand the behavior you want before you can think about implementation.

##### **Hooved** [[00:36:49](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=2209)]
I agree with that.
So my assumption was the behavior we want is to, we have a function that we're capturing, right?
And everything that function does to the state of tensors should be captured.
Like if it creates a tensor or if it modifies existing tensors,
That should be captured.
And that's what the current implementation does.
But I understand that you want to first define what you want and then implement it.

##### **Geohot** [[00:37:25](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=2245)]
Yeah.
So OK.
So how do you deal with, I mean, I wrote you those test cases, right?
So how do you deal with them in the new, how do you deal with them in the new JIT, the new JIT, all four of them?

##### **Hooved** [[00:37:37](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=2257)]
OK.
I mean, perhaps it would be easier to write that out for each test, an explanation.
So if I were to try to summarize it now, since we know what the tensors looked like before and after calling the function,
We are able to, so if you have an implicit input, for instance, an implicit input, those have to be defined in tensor graphs before you call the function.
And implicit outputs, sorry, I'm not the best.
It passes all the tests, and I'm confident it covers them all.
It would be easier for me to write this than try to ramble it off now.

##### **Geohot** [[00:38:47](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=2327)]
Yeah.
Maybe explicitly like, so there's a test in test cases called test implicit output.
And inside that function, there is a realize.
How does that work with ban realizes?
How do you get that same behavior if you're banning realizes?

##### **Hooved** [[00:39:05](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=2345)]
OK, so if we're going to focus discussion on the implicit output case, I know I looked at that in detail.
I could write it out.
But basically, you know that
You know that there was a change before and after you called the function where that tensor existed with the lazy data graph before you called the function.
And then you're assigning to it within the function.
And afterwards, that tensor now exists with a new lazy data graph that's different than it originally was.
And so you detect that change.
Because now the UOps have different memory address for lazy data before and after.
And so.

##### **Geohot** [[00:40:17](https://youtu.be/xyn3mZGiXd8?t=2417)]
I'll stop you here if you're thinking about looking at the tensor graph.
How does assign behave differently from replace?
If you look at what Replace does, Replace replaces the lazy data in a tensor.
What happens if you do Replace inside of a JIT?
This is what I mean about all these things.
Before code should be written, these cases have to be thought through.
So from what I got from what you were saying is you're saying that you want to basically look at all the tensors, you want to look at all tensors and see which ones have mutated lazy data?

##### **Hooved** [[00:41:18](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=2478)]
Yeah.

##### **Geohot** [[00:41:20](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=2480)]
Okay.
Does assign mutate the tensor?

##### **Hooved** [[00:41:31](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=2491)]
Um...I think so.
Yeah, tensor.assign, it calls uop.assign and does an assign, you know, inserts and assigns.

##### **Geohot** [[00:41:40](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=2500)]
And that mutates the tensor?

##### **Hooved** [[00:41:47](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=2507)]
The tensor's lazy data changes.

##### **Geohot** [[00:41:51](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=2511)]
The tensor's lazy data changes.
Okay.
So how does that differ from replace?
The tensor lazy data also changes on replace.

##### **Hooved** [[00:42:00](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=2520)]
Correct.
Yeah, I mean, replace and assign both change lazy data that they're called on, I believe.
So the current implementation, I mean, both of those things result in tensor lazy data changing.
So not that I'm too attached to the current approach, but the current approach detects both of those things.

##### **Geohot** [[00:42:23](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=2543)]
But should it detect a replace?

##### **Hooved** [[00:42:26](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=2546)]
Should it detect a replace?
Is that your question?

##### **Geohot** [[00:42:29](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=2549)]
Yes.

##### **Hooved** [[00:42:32](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=2552)]
OK, so now that I understand the question, I would be inclined to say so.
You want to know what the function did and reproduce it after the function.

##### **Geohot** [[00:42:47](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=2567)]
What does the current one do?
What's the current behavior?

##### **Hooved** [[00:42:51](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=2571)]
I can't answer that off the top of my head.
I have to look at it and study it.
But so I guess the meta question is, I'm not saying that's a bad question.
I'm very interested in answering that question.
But how do I answer this in the most universal sense?
How do I enumerate these questions, these cases?
How did you decide?
Yeah.

##### **Chenyu** [[00:43:22](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=2602)]
So I think, too, on a very high level, things like this, how does things like this progress?

##### **Chenyu** [[00:43:35](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=2615)]
Because this project started with WebGPU and export WebGPU stuff, right?
And now because we have exporting needs, we start to think about JIT.
I don't know.
Maybe you are more interested in the WebGPU part and less so for the JIT part.
That's why the proposal to
Yeah, so my point is we don't really want to introduce a flag so that we can build things on top of that.
Because now this flag becomes a bane that we still need to remove later.
So from our perspective, from our maintenance perspective, we definitely want things to be figured out or thought out before we merge any codes related to that.
And I don't know, maybe it needs more people's time or stuff to be done before we can merge this stuff.
So I think there are a few steps that we can do to move this forward.
For example, you can write a test that you believe needs to be ready before you can further add more codes, add those test cases, and wait until someone
Make those tests pass, then you can move on to your next steps.
Or you can be the person, in this case, try to figure stuff out.
And during this research process, be the most knowledgeable person that consider all the cases that can also work.

##### **Geohot** [[00:45:14](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=2714)]
When I look at this PR and I see these V2s everywhere, so now there's V1 and V2 behavior.
Are you saying that we should maintain both of these behaviors?
It's the same thing as the flag, and this is why things like this, you can't really merge them because now we have double we have to maintain.
We have to maintain whatever V1 did and whatever V2 did.
Another approach to this whole kind of thing is what does V1 do?
Why do we need separate tests for V1 and V2?
Do the behaviors differ?
I think the truth is we don't even really know what the behavior of V1 is.
This stuff kind of evolved organically.
So yeah, I mean, I think that the direction here is much more to document, okay, this is exactly what this behavior is.
And then after it's documented, we can decide whether we want it or we don't want it.

##### **Hooved** [[00:46:16](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=2776)]
OK, so in terms of next steps, like trying to keep this organized.

##### **Chenyu** [[00:46:28](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=2788)]
My suggestion would be to make some progress would be
So for JIT parts, understand what current behavior is and document it.
And document is almost best done by writing a test to test this behavior.
Then from the WebGPU export part, I think it's useful to, you can start to add tests like you believe should pass.
And maybe it's not currently passing in the codebase.
We can certainly merge that.
As long as it's fundamental and not go to the weed of your potential implementation details, I think we can merge those.
So we know these are the things that should be done when we decide what the new behavior should look like.

##### **Geohot** [[00:47:22](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=2842)]
I totally agree that this is a good way to move forward.
And what I'll say about this project in general is it's very hard.
You've chosen to tackle really one of the hardest pieces of Tinygrad here.
It's unfortunate.
I feel a bit bad every time.
It's like, yes, we have to move in this direction.
And I feel bad that this stuff isn't ready.
The current JIT stuff is not very good.
We don't have a spec.
We don't have an understanding of what it's doing.
But unfortunately, the way that you get out of this isn't write v2.
It's like any sort of dealing with legacy code thing.
It's like first you document each behavior, you write tests for it, and then once that's done, you can say, okay, actually, I've carefully tested this behavior.
This is what it is in v1, and I think it's wrong for reasons X, Y, and Z. So yeah, the documenting through tests, I think, is totally the right approach.

##### **Hooved** [[00:48:37](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=2917)]
So I could continue to tackle that, but do we want documentation and research and a well-researched thing, do we want that to gate the web GPU stuff?
Should I just get rid of the, I'd be happy to get rid of the, or sort of not try to merge this V2 stuff, just use the current stuff, merge the web GPU stuff on that.

##### **Chenyu** [[00:49:09](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=2949)]
The thing is, we are on this developing principle to write the best way possible.
So yes, it might make you feel a sense of accomplishment if you just merge it on top of the current stuff.
But we are going to remove the current stuff in three months or six months.
Then at the time, more things need to be redone.
And that doesn't really make sense.
So if you say this is gating, yeah, I would support gating it on this.
It might not be you.
It might be someone else.
But we certainly need to figure this out before we have the best version we can have.
And it really is what it is.

##### **Hooved** [[00:49:58](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=2998)]
So what if it were sufficiently factored out that the WebGPU stuff you merged didn't have to change much or probably wouldn't change much?

##### **Geohot** [[00:50:09](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=3009)]
It's not about whether it changes.
It's not about whether it changes.
It's about building on a foundation that's going to be ripped out.
And then we have to carefully put supports up to hold up each piece of that thing while we rip the foundation out.
And it makes the foundation
Replacement project, more expensive.

##### **Chenyu** [[00:50:34](https://youtu.be/xyn3mZGiXd8?t=3040)]
So far, what we have gotten from this process is we know how hard it is.
And I guess we promised you that this would be good in a few months.
And if you are interested, feel free to tackle this problem, continue working on the problem.
Otherwise, I think just document what needs to be done for you to add web GPU export.
And we will think about how to work on it.
But as George said, I think the best I can put is we are not ready for it.
So we really want to be ready for it.
Unfortunately, we are not yet.

##### **Chenyu** [[00:51:22](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=3082)]
OK.

##### **Geohot** [[00:51:25](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=3085)]
I think there's two ways to go about this.
Either keep working on the v2 JIT, but accept that it's going to be really, really hard.
And anything that looks like an if statement between v1 and v2, we can't merge that.
What we have to do is remove v1 in order to build v2.
And yes, that's going to be extremely hard.
But there's no way around it.
The other option is just to be like, look, I got the web GPU stuff done in three months.
Here's what I need.
When you guys are ready with the V2 stuff, I'll update it for the V2 stuff.
But I totally think the JIT refactor is definitely outside the scope of the bounty.
And again, I'm sorry that our stuff's not ready.
And I appreciate you trying to work on it.
But the only way that we're going to be able to get this merged is with
A deletion of V1 and a replacement with V2.
And the only way to do that is to document all of V1 and yeah.

##### **Hooved** [[00:52:28](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=3148)]
That's what I'm looking for.
Thank you for, that's what I was looking for.
So, okay.
I can try to tackle that and see if it'll work.

##### **Geohot** [[00:52:42](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=3162)]
I can start researching.
What I will say about,
What I will say about this project is you will learn a lot doing it, and there is no easy solution to this.
It's just like, okay, what do we do about realizes and JITs?
Is this approach of using the all tensors thing good?
I'm worried about that, right?
You have this thing where you take all tensors before and all tensors after.
Well, which tensors can change?
Maybe the right thing to do is to hook assign, but I'm not sure that's the right thing to do.
That's the kind of like, you know.

##### **Hooved** [[00:53:13](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=3193)]
I have a principled argument about that, but we're sort of running out of time.

##### **Chenyu** [[00:53:17](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=3197)]
Yeah.
OK, let's conclude this.
I think one specific thing is, if I'm working on this, I will also check how JAX does it, because I know they make some .

##### **Hooved** [[00:53:31](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=3211)]
As an input.

##### **Chenyu** [[00:53:33](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=3213)]
They make that trade-off for their JIT and assign.
Not clear.
Maybe we want to do that.
Maybe we don't.
But that's another reference point that we're looking to.

##### **Chenyu** [[00:53:47](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=3227)]
Okay.

##### **Chenyu** [[00:53:49](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=3229)]
With that, we'll have the symbolic list stuff from S-Lykles.

##### **Sied Lykles** [[00:54:01](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=3241)]
Hey, hi.
Sorry, yeah.
Yeah, I don't really have much to add.
You merged the symbolic fuzzer, I guess the one that replaced the old fuzzer.
I know what I want, to test individual rewrite rules, but I don't have time for that.

##### **Chenyu** [[00:54:21](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=3261)]
Okay, no worries.
For other bounties, we have a PR for lm-eval.

##### **Chenyu** [[00:54:36](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=3276)]
At least it runs.
I'm pretty sure it runs.
I was trying that on a Redbox.
Then I hit a bunch of issues.
I'll probably move on to a Greenbox or Mac.
I think the script is right.
That's the bounty.
I will see how fast we can run that and if we can add that to some kind of a CI job to monitor that.

##### **Chenyu** [[00:55:03](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=3303)]
And we have AMD LLVM

##### **Chenyu** [[00:55:10](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=3310)]
Almost work.
I think it's like a few percent slower, but in the spirit of bringing more stuff to Tinygrad, if it's only a few percent slower, I think it's fine to make it default.
One thing I need to check was the MI300x, if it runs correctly.
But I think that's the last thing before we can merge.

##### **Chenyu** [[00:55:30](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=3330)]
We can make that default.

##### **Geohot** [[00:55:34](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=3334)]
For AMD LLVM, I'd like to see a whole sort of refactor
We have multiple things like PTX and CUDA, which are the same backend, but different compilers.
CPU and LLVM are also this.
And I'd like to see that kind of refactored where you can independently choose the runtime and the compiler.
Like we have like the device, and the device is like, the device kind of is memory.
More so than a compiler.
So we have like two devices now, one called CPU and one called LLVM.
These are the same device, right?
They both run on the CPU.
They both use the CPU's memory.
The only difference is the compiler.
It would be great to see this refactored into a device and compiler.

##### **Chenyu** [[00:56:22](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=3382)]
That feels like the same direction as the cloud issue.
Cloud, you also want to be more explicitly specify a compiler.
Yeah.
OK, I think that's something we can add on top of your short write up for your Cloud need.
Then we can see what components needs to be factored out.

##### **Chenyu** [[00:56:49](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=3409)]
Cloud was for Uuuvn stuff, but he gave some updates already.

##### **Geohot** [[00:57:01](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=3421)]
Yeah, last week we got all six red machines connected on the 100 gig network, so it should be easy to test everything on there.

##### **Chenyu** [[00:57:17](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=3437)]
Great.
We want to quickly mention the HLB-CIFAR one.

##### **Chenyu** [[00:57:33](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=3453)]
Oh, there are multiple PRs on that.

##### **Geohot** [[00:57:39](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=3459)]
There's like five.

##### **Chenyu** [[00:57:42](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=3462)]
And everyone kind of does part of it and asks for benchmark numbers.

##### **Chenyu** [[00:57:46](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=3466)]
I don't know if they reply to me.

##### **Geohot** [[00:57:57](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=3477)]
Yeah, for that one, I see the five PRs.
They're all very mediocre quality, like
I don't know.
Let's wait a week and then we'll review the best one.

##### **Geohot** [[00:58:10](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=3490)]
To everybody who's listening here, please don't use AI.
If you submit stuff that you just copy and paste it from AI, I know you're wasting everybody's time.
Please don't do it.
If you're not going to put in the effort, just don't do it.

##### **Chenyu** [[00:58:32](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=3512)]
Using AI to understand what's going on is great.
Using AI to improve your knowledge is great.
Maybe even use AI for drafting is fine.
But at the end of the day, we accept good PRs.
If your AI can make good PRs, I doubt we care.
But for now, it's not doing that.

##### **Geohot** [[00:58:52](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=3532)]
That's true.
We do not discriminate between silicon and human-based life, but we do discriminate against low-quality PRs, like the kind generated by Codex and GPT.

##### **Chenyu** [[00:59:03](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=3543)]
Yeah, and if there are stuff that's too slow, we probably need to fix that.

##### **Chenyu** [[00:59:15](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=3555)]
I don't have a better answer for you.
You say that was too slow, so either someone needs to fix that.

##### **Chenyu** [[00:59:25](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=3565)]
OK.

##### **Chenyu** [[00:59:28](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=3568)]
That was this meeting.
Thanks, everyone.
And let's make CI works better, more better user experience and better developer experience.
And that's it for this week.

##### **Chenyu** [[00:59:44](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=3584)]
Bye.

##### **Geohot** [[00:59:45](https://www.youtube.com/watch?v=xyn3mZGiXd8&t=3585)]
Absolutely.
All green check marks.
Bye bye.
Bye.