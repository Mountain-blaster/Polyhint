# Character Counter for jQuery

The jQuery Character Counter Plugin is simple character counter for your forms.

![alt tag](https://raw.githubusercontent.com/kokulusilgi/Character-Counter-Plugin-for-jQuery/master/character-counter-plugin-jquery.png)

## Demo
http://kokulusilgi.com/jquery-character-counter/

## Getting Started

Add jquery.charactercounter.js to your project.

```
<form>
    <div class="form-group">
        <label>Foo</label>
        <input id="textInput" class="form-control" type="text">
    </div>
    <div class="form-group">
        <label>Foo 2</label>
        <textarea id="textareaInput" class="form-control"></textarea>
    </div>
</form>
<script src="jquery.js"></script>
<script src="jquery.charactercounter.js"></script>
<script>
$('#textInput').characterCounter(75);
$('#textareaInput').characterCounter(150);
</script>
```

License
----

MIT

[@kokulusilgi]:http://twitter.com/kokulusilgi
