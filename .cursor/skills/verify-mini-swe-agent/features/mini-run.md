# Local agent run (`mini`)

## Sub-features
- Text-based model path (`DeterministicModel`). Observations come back as `user` messages.
- Tool-call path (`DeterministicToolcallModel`, the shape the default `mini.yaml` + litellm produces). Observations come back as `tool` messages.
- Submission: the first output line is `COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT`, and the rest becomes `info.submission`.
- The trajectory is saved with `-o`.

## How to get to it (user POV)
`mini -t "<task>" -y`, with a model set in the global config. Offline, the model comes from a scenario `-c` file instead.

## Driving it with drive.sh
- `drive.sh submit` should show Submitted, `submission "verify-ok\n"`, `api_calls 2`, and `proof.txt` containing `hello-from-verify` in workdir_files.txt.
- `drive.sh toolcall` should show Submitted, roles `system,user,assistant,tool,assistant,tool,exit`, and `proof.txt` containing `toolcall-ok`.

## Gotchas
- Without `--exit-immediately` the interactive agent asks for confirmation before exiting. drive.sh feeds `</dev/null`, so a missing flag shows up as an odd exit rather than a hang.
- A toolcall action without a matching `tool_call_id` breaks observation formatting.
