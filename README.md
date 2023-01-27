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
* [ ] Consider using basicSetup instead of minimalSetup but without line numbers to benefit from more features
* [ ] Prompt enhancement

### "performance"

* [ ] normalise the prompts (to prevent generating the same prompt twice basically) This could be done by using the tokenizer used by stable diffusion like that it's only when it's literally exactly the same thing (although we don't know how vana does its tokenizing especially with the {target_token} thing)o

### Visual

* [ ] Change font for text editor

## feedback to Vana

* There is clearly a security issue with your codes
* in the examples, some get request use the "content-type" header when it
  doesn't make sense to set the content type for a GET request
* even when an exhibit doesn't exist success is returned (but with empty pictures)
