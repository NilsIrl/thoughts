# Thoughts (temporary name)

## Usage

```
npm i
npm run build
flask --app hackathon --debug run
```

## TODO

### features

* [ ] Decide whether we want people to follow each other, or be friends with each other, .... (pros of following is that it allows to have granularity where a person can generate stuff about another person when the other can't and then like that we can have private account like on instagram where people can "request" to follow)


### "performance"

* [ ]: normalise the prompts (to prevent generating the same prompt twice basically) This could be done by using the tokenizer used by stable diffusion like that it's only when it's literally exactly the same thing (although we don't know how vana does its tokenizing especially with the {target_token} thing)o

## feedback to Vana

* There is clearly a security issue with your codes
* in the examples, some get request use the "content-type" header when it
  doesn't make sense to set the content type for a GET request
* even when an exhibit doesn't exist success is returned (but with empty pictures)
