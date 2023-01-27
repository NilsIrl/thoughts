# Thoughts (temporary name)

## Usage

```
npm i
npm run build
flask --app hackathon init-db
flask --app hackathon --debug run
```

## TODO

### features

* [ ] Remove the gutter and change the font for the text editor
* [ ] Make it possible to use "I" instead of @ your own email address
* [ ] Decide whether we want people to follow each other, or be friends with each other, .... (pros of following is that it allows to have granularity where a person can generate stuff about another person when the other can't and then like that we can have private account like on instagram where people can "request" to follow)
* [ ] Consider using basicSetup instead of minimalSetup but without line numbers to benefit from more features
* [ ] Test synchroneous API
* [ ] Prompt enhancement
* [ ] We should probably enable line wrapping on the editor

### "performance"

* [ ] normalise the prompts (to prevent generating the same prompt twice basically) This could be done by using the tokenizer used by stable diffusion like that it's only when it's literally exactly the same thing (although we don't know how vana does its tokenizing especially with the {target_token} thing)o

### Visual

* [ ] There is no space between the 2 input fields for logging in.
* [ ] Change font for text editor

## feedback to Vana

* There is clearly a security issue with your codes
* in the examples, some get request use the "content-type" header when it
  doesn't make sense to set the content type for a GET request
* even when an exhibit doesn't exist success is returned (but with empty pictures)
