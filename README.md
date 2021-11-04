# Cadence

A rhythm analysis toolkit, gathering multiple parsing engines:
* [Prosodic](https://github.com/quadrismegistus/prosodic) for fast English and Finnish metrical scansion.
* Cadence itself for slower but exhaustive, MaxEnt-able metrical scansion.

## Quickstart

### Install

#### 1. Install python package
```
# install from github
pip install -U git+https://github.com/quadrismegistus/cadence
```

#### 2. Insteall espeak (TTS)

Install espeak, free TTS software, to 'sound out' unknown words. See [here](http://espeak.sourceforge.net/download.html) for all downloads. For Mac or Linux, you can use:
```
apt-get install espeak     # linux
brew install espeak        # mac
```

### Load texts


```python
sonnetXIV = """Not from the stars do I my judgement pluck;
And yet methinks I have astronomy,
But not to tell of good or evil luck,
Of plagues, of dearths, or seasons' quality;
Nor can I fortune to brief minutes tell,
Pointing to each his thunder, rain and wind,
Or say with princes if it shall go well
By oft predict that I in heaven find:
But from thine eyes my knowledge I derive,
And constant stars in them I read such art
As 'truth and beauty shall together thrive,
If from thyself, to store thou wouldst convert';
    Or else of thee this I prognosticate:
    'Thy end is truth's and beauty's doom and date.'
"""

melville="""Is it that by its indefiniteness it shadows forth the heartless voids and immensities of the universe, and thus stabs us from behind with the thought of annihilation, when beholding the white depths of the milky way? Or is it, that as in essence whiteness is not so much a colour as the visible absence of colour; and at the same time the concrete of all colours; is it for these reasons that there is such a dumb blankness, full of meaning, in a wide landscape of snows: a colourless, all-colour of atheism from which we shrink?"""
```


```python
# this should work following installation
import cadence as cd
```


```python
# These are identical
sonnet = cd.Text(sonnetXIV, verse=True)
sonnet = cd.Text(sonnetXIV, linebreaks=True, phrasebreaks=False)
sonnet = cd.Poem(sonnetXIV)
```


```python
# So are these
para = cd.Text(melville, prose=True)
para = cd.Text(melville, linebreaks=False, phrasebreaks=True)
para = cd.Prose(melville)
```

### Syllabify


```python
# scansion by syllable
sonnet.scan()
```

    Iterating over line scansions [x1]: 100%|██████████| 14/14 [00:00&lt;00:00, 56.28it/s]





</p><div>

<table border="1" class="dataframe">
<thead>
<tr style="text-align: right;">
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th>is_funcword</th>
<th>is_heavy</th>
<th>is_light</th>
<th>is_peak</th>
<th>is_stressed</th>
<th>is_syll</th>
<th>is_trough</th>
<th>is_unstressed</th>
<th>line_num_syll</th>
<th>prom_strength</th>
<th>prom_stress</th>
<th>prom_weight</th>
</tr>
<tr>
<th>stanza_i</th>
<th>line_i</th>
<th>linepart_i</th>
<th>line_str</th>
<th>word_i</th>
<th>word_str</th>
<th>word_ipa_i</th>
<th>word_ipa</th>
<th>syll_i</th>
<th>syll_str</th>
<th>syll_ipa</th>
<th>syll_stress</th>
<th>syll_weight</th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<th rowspan="11" valign="top">1</th>
<th rowspan="5" valign="top">1</th>
<th rowspan="5" valign="top">1</th>
<th rowspan="5" valign="top">Not from the stars do I my judgement pluck;</th>
<th rowspan="2" valign="top">1</th>
<th rowspan="2" valign="top">Not</th>
<th>1</th>
<th>'nɑt</th>
<th>1</th>
<th>Not</th>
<th>'nɑt</th>
<th>P</th>
<th>H</th>
<td>1</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>1</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>10</td>
<td>NaN</td>
<td>1.0</td>
<td>1</td>
</tr>
<tr>
<th>2</th>
<th>nɑt</th>
<th>1</th>
<th>Not</th>
<th>nɑt</th>
<th>U</th>
<th>H</th>
<td>1</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>0</td>
<td>1</td>
<td>0</td>
<td>1</td>
<td>10</td>
<td>NaN</td>
<td>0.0</td>
<td>1</td>
</tr>
<tr>
<th>2</th>
<th>from</th>
<th>1</th>
<th>frʌm</th>
<th>1</th>
<th>from</th>
<th>frʌm</th>
<th>U</th>
<th>H</th>
<td>1</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>0</td>
<td>1</td>
<td>0</td>
<td>1</td>
<td>10</td>
<td>NaN</td>
<td>0.0</td>
<td>1</td>
</tr>
<tr>
<th>3</th>
<th>the</th>
<th>1</th>
<th>ðə</th>
<th>1</th>
<th>the</th>
<th>ðə</th>
<th>U</th>
<th>L</th>
<td>1</td>
<td>0</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>1</td>
<td>0</td>
<td>1</td>
<td>10</td>
<td>NaN</td>
<td>0.0</td>
<td>0</td>
</tr>
<tr>
<th>4</th>
<th>stars</th>
<th>1</th>
<th>'stɑrz</th>
<th>1</th>
<th>stars</th>
<th>'stɑrz</th>
<th>P</th>
<th>H</th>
<td>0</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>1</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>10</td>
<td>NaN</td>
<td>1.0</td>
<td>1</td>
</tr>
<tr>
<th>...</th>
<th>...</th>
<th>...</th>
<th>...</th>
<th>...</th>
<th>...</th>
<th>...</th>
<th>...</th>
<th>...</th>
<th>...</th>
<th>...</th>
<th>...</th>
<td>...</td>
<td>...</td>
<td>...</td>
<td>...</td>
<td>...</td>
<td>...</td>
<td>...</td>
<td>...</td>
<td>...</td>
<td>...</td>
<td>...</td>
<td>...</td>
</tr>
<tr>
<th rowspan="5" valign="top">14</th>
<th rowspan="5" valign="top">1</th>
<th rowspan="5" valign="top">'Thy end is truth's and beauty's doom and date.'</th>
<th rowspan="2" valign="top">6</th>
<th rowspan="2" valign="top">beauty's</th>
<th rowspan="2" valign="top">1</th>
<th rowspan="2" valign="top">'bjʉː.tɪz</th>
<th>1</th>
<th>beau</th>
<th>'bjʉː</th>
<th>P</th>
<th>L</th>
<td>0</td>
<td>0</td>
<td>1</td>
<td>1</td>
<td>1</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>10</td>
<td>1.0</td>
<td>1.0</td>
<td>0</td>
</tr>
<tr>
<th>2</th>
<th>ty's</th>
<th>tɪz</th>
<th>U</th>
<th>H</th>
<td>0</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>0</td>
<td>1</td>
<td>1</td>
<td>1</td>
<td>10</td>
<td>0.0</td>
<td>0.0</td>
<td>1</td>
</tr>
<tr>
<th>7</th>
<th>doom</th>
<th>1</th>
<th>'duːm</th>
<th>1</th>
<th>doom</th>
<th>'duːm</th>
<th>P</th>
<th>H</th>
<td>0</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>1</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>10</td>
<td>NaN</td>
<td>1.0</td>
<td>1</td>
</tr>
<tr>
<th>8</th>
<th>and</th>
<th>1</th>
<th>ænd</th>
<th>1</th>
<th>and</th>
<th>ænd</th>
<th>U</th>
<th>H</th>
<td>1</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>0</td>
<td>1</td>
<td>0</td>
<td>1</td>
<td>10</td>
<td>NaN</td>
<td>0.0</td>
<td>1</td>
</tr>
<tr>
<th>9</th>
<th>date.'</th>
<th>1</th>
<th>'deɪt</th>
<th>1</th>
<th>date.'</th>
<th>'deɪt</th>
<th>P</th>
<th>H</th>
<td>0</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>1</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>10</td>
<td>NaN</td>
<td>1.0</td>
<td>1</td>
</tr>
</tbody>
</table>
<p>156 rows × 12 columns</p>
</div>




```python
para.scan()
```

    Iterating over line scansions [x1]: 100%|██████████| 11/11 [00:00&lt;00:00, 54.91it/s]





<div>

<table border="1" class="dataframe">
<thead>
<tr style="text-align: right;">
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th>is_funcword</th>
<th>is_heavy</th>
<th>is_light</th>
<th>is_peak</th>
<th>is_stressed</th>
<th>is_syll</th>
<th>is_trough</th>
<th>is_unstressed</th>
<th>line_num_syll</th>
<th>prom_strength</th>
<th>prom_stress</th>
<th>prom_weight</th>
</tr>
<tr>
<th>stanza_i</th>
<th>line_i</th>
<th>linepart_i</th>
<th>line_str</th>
<th>word_i</th>
<th>word_str</th>
<th>word_ipa_i</th>
<th>word_ipa</th>
<th>syll_i</th>
<th>syll_str</th>
<th>syll_ipa</th>
<th>syll_stress</th>
<th>syll_weight</th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<th rowspan="11" valign="top">1</th>
<th rowspan="5" valign="top">1</th>
<th rowspan="5" valign="top">1</th>
<th rowspan="5" valign="top">Is it that by its indefiniteness it shadows forth the heartless voids and immensities of the universe,</th>
<th>1</th>
<th>Is</th>
<th>1</th>
<th>ɪz</th>
<th>1</th>
<th>Is</th>
<th>ɪz</th>
<th>U</th>
<th>H</th>
<td>1</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>0</td>
<td>1</td>
<td>0</td>
<td>1</td>
<td>28</td>
<td>NaN</td>
<td>0.0</td>
<td>1</td>
</tr>
<tr>
<th>2</th>
<th>it</th>
<th>1</th>
<th>ɪt</th>
<th>1</th>
<th>it</th>
<th>ɪt</th>
<th>U</th>
<th>H</th>
<td>1</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>0</td>
<td>1</td>
<td>0</td>
<td>1</td>
<td>28</td>
<td>NaN</td>
<td>0.0</td>
<td>1</td>
</tr>
<tr>
<th rowspan="2" valign="top">3</th>
<th rowspan="2" valign="top">that</th>
<th>1</th>
<th>'ðæt</th>
<th>1</th>
<th>that</th>
<th>'ðæt</th>
<th>P</th>
<th>H</th>
<td>1</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>1</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>28</td>
<td>NaN</td>
<td>1.0</td>
<td>1</td>
</tr>
<tr>
<th>2</th>
<th>ðət</th>
<th>1</th>
<th>that</th>
<th>ðət</th>
<th>U</th>
<th>H</th>
<td>1</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>0</td>
<td>1</td>
<td>0</td>
<td>1</td>
<td>28</td>
<td>NaN</td>
<td>0.0</td>
<td>1</td>
</tr>
<tr>
<th>4</th>
<th>by</th>
<th>1</th>
<th>baɪ</th>
<th>1</th>
<th>by</th>
<th>baɪ</th>
<th>U</th>
<th>L</th>
<td>1</td>
<td>0</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>1</td>
<td>0</td>
<td>1</td>
<td>28</td>
<td>NaN</td>
<td>0.0</td>
<td>0</td>
</tr>
<tr>
<th>...</th>
<th>...</th>
<th>...</th>
<th>...</th>
<th>...</th>
<th>...</th>
<th>...</th>
<th>...</th>
<th>...</th>
<th>...</th>
<th>...</th>
<th>...</th>
<td>...</td>
<td>...</td>
<td>...</td>
<td>...</td>
<td>...</td>
<td>...</td>
<td>...</td>
<td>...</td>
<td>...</td>
<td>...</td>
<td>...</td>
<td>...</td>
</tr>
<tr>
<th rowspan="5" valign="top">2</th>
<th rowspan="5" valign="top">8</th>
<th rowspan="5" valign="top">all-colour of atheism from which we shrink?</th>
<th>4</th>
<th>from</th>
<th>1</th>
<th>frʌm</th>
<th>1</th>
<th>from</th>
<th>frʌm</th>
<th>U</th>
<th>H</th>
<td>1</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>0</td>
<td>1</td>
<td>0</td>
<td>1</td>
<td>12</td>
<td>NaN</td>
<td>0.0</td>
<td>1</td>
</tr>
<tr>
<th rowspan="2" valign="top">5</th>
<th rowspan="2" valign="top">which</th>
<th>1</th>
<th>'wɪʧ</th>
<th>1</th>
<th>which</th>
<th>'wɪʧ</th>
<th>P</th>
<th>H</th>
<td>1</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>1</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>12</td>
<td>NaN</td>
<td>1.0</td>
<td>1</td>
</tr>
<tr>
<th>2</th>
<th>wɪʧ</th>
<th>1</th>
<th>which</th>
<th>wɪʧ</th>
<th>U</th>
<th>H</th>
<td>1</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>0</td>
<td>1</td>
<td>0</td>
<td>1</td>
<td>12</td>
<td>NaN</td>
<td>0.0</td>
<td>1</td>
</tr>
<tr>
<th>6</th>
<th>we</th>
<th>1</th>
<th>wiː</th>
<th>1</th>
<th>we</th>
<th>wiː</th>
<th>U</th>
<th>L</th>
<td>1</td>
<td>0</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>1</td>
<td>0</td>
<td>1</td>
<td>12</td>
<td>NaN</td>
<td>0.0</td>
<td>0</td>
</tr>
<tr>
<th>7</th>
<th>shrink?</th>
<th>1</th>
<th>'ʃrɪŋk</th>
<th>1</th>
<th>shrink?</th>
<th>'ʃrɪŋk</th>
<th>P</th>
<th>H</th>
<td>0</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>1</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>12</td>
<td>NaN</td>
<td>1.0</td>
<td>1</td>
</tr>
</tbody>
</table>
<p>152 rows × 12 columns</p>
</div>



### Parse text


```python
# Parse lines (verse)
sonnet.parse()
```


Not <i><b>fróm</b></i> the <b>stárs</b> do <i><b>Í</b></i> my <b>júdge</b>ment <b>plúck</b>;



And <b>yét</b> me<b>thínks</b> I <b>háve</b> as<b>trón</b>o<i><b>mý</b></i>,



But <b>nót</b> to <b>téll</b> of <b>góod</b> or <b>év</b>il <b>lúck</b>,



Of <b>plágues</b>, of <b>déarths</b>, or <b>séa</b>son <b>qúal</b>i<i><b>tý</b></i>;



Nor <i><b>cán</b></i> I <b>fór</b>tune <i><b>tó</b></i> <i>brief</i> <b>mín</b>utes <b>téll</b>,



<b>Póint</b><i>ing</i> <i>to</i> <b>éach</b> his <b>thún</b>der, <b>ráin</b> and <b>wínd</b>,



Or <b>sáy</b> with <b>prí</b>nces <i><b>íf</b></i> it <b>sháll</b> <i>go</i> <b>wéll</b>



By <b>óft</b> pre<b>díct</b> that <i><b>Í</b></i> in <b>héav</b>en <b>fínd</b>:



But <i><b>fróm</b></i> thine <b>éyes</b> my <b>knówl</b>edge <i><b>Í</b></i> de<b>ríve</b>,



And <b>cón</b>stant <b>stárs</b> in <i><b>thém</b></i> I <b>réad</b> such <b>árt</b>



As <b>'trúth</b> and <b>béau</b>ty <b>sháll</b> to<b>géth</b>er <b>thríve</b>,



If <i><b>fróm</b></i> thy<b>sélf</b>, to <b>stóre</b> thou <b>wóuldst</b> con<b>vért'</b>;



Or <b>élse</b> of <i><b>thée</b></i> this <i><b>Í</b></i> <i>prog</i><b>nós</b>ti<b>cáte</b>:



'Thy <b>énd</b> is <b>trúth's</b> and <b>béau</b>ty's <b>dóom</b> and <b>dáte</b>.'



```python
# Parse sentences (prose)
para.parse()
```


<i><b>Ís</b></i> it <b>thát</b> by <i><b>íts</b></i> in<b>déf</b>i<i><b>níte</b></i><i>ness</i> <i>it</i> <b>shád</b><i>ows</i> <b>fórth</b> the <b>héart</b>less <b>vóids</b> <i>and</i> <i>im</i><b>mén</b>si<i><b>tíes</b></i> <i>of</i> <i>the</i> <b>úni</b>ver<b>sé</b>, and <i><b>thús</b></i> <i><b>stábs</b></i> us <i><b>fróm</b></i> be<b>hínd</b> <i>with</i> <i>the</i> <b>thóught</b> <i>of</i> <i>an</i><b>ní</b>hi<b>lá</b>tion, <b>whén</b> be<b>hóld</b>ing <i><b>thé</b></i> <i>white</i> <b>dépths</b> <i>of</i> <i>the</i> <b>mí</b>lky <b>wáy</b>?



Or <i><b>ís</b></i> it, <b>thát</b> <i>as</i> <i>in</i> <b>éss</b>ence <b>whíte</b><i>ness</i> <i>is</i> <b>nót</b> so <b>múch</b> a <b>cól</b>our <i><b>ás</b></i> the <b>vís</b><i>i</i><i>ble</i> <b>áb</b><i>sence</i> <i>of</i> <b>cól</b>our; and <b>át</b> the <i><b>sáme</b></i> <i><b>tíme</b></i> the <b>cón</b>crete <i><b>óf</b></i> all <b>cólo</b>urs; <i><b>ís</b></i> it <i><b>fór</b></i> these <b>réa</b>sons <b>thát</b> there <i><b>ís</b></i> such <i><b>á</b></i> <i>dumb</i> <b>blánk</b>ness, <b>fúll</b> of <b>méan</b>ing, <b>ín</b> a <b>wíde</b> <i>land</i><b>scápe</b> of <b>snóws</b>: a <b>cólour</b>le<i><b>ss</b></i>, al<b>l</b>-colour <i><b>óf</b></i> athe<b>í</b><i>sm</i> <i>from</i> <b>whích</b> we <b>shrínk</b>?



```python
# get parse data as dataframe
sonnet.parses()                  # plausible (unbounded) parses
sonnet.unbounded_parses()        # same as above
sonnet.all_parses()              # all parses, plausible or no
sonnet.best_parses()             # only top ranking parse per line
```




<div>

<table border="1" class="dataframe">
<thead>
<tr style="text-align: right;">
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th>*total</th>
<th>*s/unstressed</th>
<th>*w-res</th>
<th>*w/stressed</th>
<th>*clash</th>
<th>*f-res</th>
<th>*w/peak</th>
<th>*lapse</th>
<th>is_funcword</th>
<th>is_heavy</th>
<th>is_light</th>
<th>is_peak</th>
<th>is_s</th>
<th>is_stressed</th>
<th>is_syll</th>
<th>is_trough</th>
<th>is_unstressed</th>
<th>is_w</th>
<th>line_num_syll</th>
<th>parse_num_pos</th>
<th>parse_num_syll</th>
<th>parse_rank_dense</th>
<th>parse_rank_min</th>
<th>prom_strength</th>
<th>prom_stress</th>
<th>prom_weight</th>
</tr>
<tr>
<th>stanza_i</th>
<th>line_i</th>
<th>linepart_i</th>
<th>line_str</th>
<th>parse_rank</th>
<th>parse_str</th>
<th>parse</th>
<th>parse_i</th>
<th>combo_stress</th>
<th>combo_ipa</th>
<th>combo_i</th>
<th>parse_is_bounded</th>
<th>parse_bounded_by</th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<th rowspan="14" valign="top">1</th>
<th>1</th>
<th>1</th>
<th>Not from the stars do I my judgement pluck;</th>
<th>1</th>
<th>not FROM* the STARS do I* my JUDGE ment PLUCK;</th>
<th>w s w s w s w s w s</th>
<th>1</th>
<th>U U U P U U U P U P</th>
<th>nɑt frʌm ðə 'stɑrz duː aɪ maɪ 'ʤʌʤ.mənt 'plʌk</th>
<th>1</th>
<th>False</th>
<th></th>
<td>2.0</td>
<td>2.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>6</td>
<td>6</td>
<td>4</td>
<td>1</td>
<td>5</td>
<td>3</td>
<td>10</td>
<td>1</td>
<td>7</td>
<td>5</td>
<td>10</td>
<td>10</td>
<td>19</td>
<td>1</td>
<td>1</td>
<td>1.0</td>
<td>3.0</td>
<td>6</td>
</tr>
<tr>
<th>2</th>
<th>1</th>
<th>And yet methinks I have astronomy,</th>
<th>1</th>
<th>and YET me THINKS i HAVE as TRON o MY,*</th>
<th>w s w s w s w s w s</th>
<th>0</th>
<th>U P U P U P U P U U</th>
<th>ænd 'jɛt mi.'θɪŋks aɪ 'hæv ə.'strɑ.nʌ.miː</th>
<th>0</th>
<th>False</th>
<th></th>
<td>1.0</td>
<td>1.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>3</td>
<td>4</td>
<td>6</td>
<td>2</td>
<td>5</td>
<td>4</td>
<td>10</td>
<td>3</td>
<td>6</td>
<td>5</td>
<td>10</td>
<td>10</td>
<td>19</td>
<td>1</td>
<td>1</td>
<td>2.0</td>
<td>4.0</td>
<td>4</td>
</tr>
<tr>
<th>3</th>
<th>1</th>
<th>But not to tell of good or evil luck,</th>
<th>1</th>
<th>but NOT to TELL of GOOD or EV il LUCK,</th>
<th>w s w s w s w s w s</th>
<th>0</th>
<th>U P U P U P U P U P</th>
<th>bət 'nɑt tuː 'tɛl ʌv 'gʊd ɔːr 'iː.vəl 'lək</th>
<th>0</th>
<th>False</th>
<th></th>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>5</td>
<td>8</td>
<td>2</td>
<td>1</td>
<td>5</td>
<td>5</td>
<td>10</td>
<td>1</td>
<td>5</td>
<td>5</td>
<td>10</td>
<td>10</td>
<td>19</td>
<td>1</td>
<td>1</td>
<td>1.0</td>
<td>5.0</td>
<td>8</td>
</tr>
<tr>
<th>4</th>
<th>1</th>
<th>Of plagues, of dearths, or seasons' quality;</th>
<th>1</th>
<th>of PLAGUES, of DEARTHS, or SEA son QUAL i TY;*</th>
<th>w s w s w s w s w s</th>
<th>0</th>
<th>U P U P U P U P U U</th>
<th>ʌv 'pleɪgz ʌv 'dəːθs ɔːr 'siː.zənz 'kwɑ.lə.tiː</th>
<th>0</th>
<th>False</th>
<th></th>
<td>1.0</td>
<td>1.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>3</td>
<td>6</td>
<td>4</td>
<td>2</td>
<td>5</td>
<td>4</td>
<td>10</td>
<td>2</td>
<td>6</td>
<td>5</td>
<td>10</td>
<td>10</td>
<td>19</td>
<td>1</td>
<td>1</td>
<td>2.0</td>
<td>4.0</td>
<td>6</td>
</tr>
<tr>
<th>5</th>
<th>1</th>
<th>Nor can I fortune to brief minutes tell,</th>
<th>1</th>
<th>nor CAN* i FOR tune TO* brief* MIN utes TELL,</th>
<th>w s w s w s w s w s</th>
<th>0</th>
<th>U U U P U U P P U P</th>
<th>nɔːr kæn aɪ 'fɔːr.ʧən tuː 'briːf 'mɪ.nʌts 'tɛl</th>
<th>0</th>
<th>False</th>
<th></th>
<td>3.0</td>
<td>2.0</td>
<td>0.0</td>
<td>1.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>4</td>
<td>7</td>
<td>3</td>
<td>2</td>
<td>5</td>
<td>4</td>
<td>10</td>
<td>2</td>
<td>6</td>
<td>5</td>
<td>10</td>
<td>10</td>
<td>19</td>
<td>1</td>
<td>1</td>
<td>2.0</td>
<td>4.0</td>
<td>7</td>
</tr>
<tr>
<th>6</th>
<th>1</th>
<th>Pointing to each his thunder, rain and wind,</th>
<th>1</th>
<th>POINT ing.to* EACH his THUN der, RAIN and WIND,</th>
<th>s w w s w s w s w s</th>
<th>0</th>
<th>P U U P U P U P U P</th>
<th>'pɔɪn.tɪŋ tuː 'iːʧ hɪz 'θʌn.dɛː 'reɪn ænd 'waɪnd</th>
<th>0</th>
<th>False</th>
<th></th>
<td>2.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>2.0</td>
<td>0.0</td>
<td>0.0</td>
<td>4</td>
<td>8</td>
<td>2</td>
<td>2</td>
<td>5</td>
<td>5</td>
<td>10</td>
<td>2</td>
<td>5</td>
<td>5</td>
<td>10</td>
<td>9</td>
<td>19</td>
<td>1</td>
<td>1</td>
<td>2.0</td>
<td>5.0</td>
<td>8</td>
</tr>
<tr>
<th>7</th>
<th>1</th>
<th>Or say with princes if it shall go well</th>
<th>1</th>
<th>or SAY with PRI nces IF* it SHALL go* WELL</th>
<th>w s w s w s w s w s</th>
<th>0</th>
<th>U P U P U U U P P P</th>
<th>ɔːr 'seɪ wɪð 'prɪn.səz ɪf ɪt 'ʃæl 'goʊ 'wɛl</th>
<th>0</th>
<th>False</th>
<th></th>
<td>2.0</td>
<td>1.0</td>
<td>0.0</td>
<td>1.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>4</td>
<td>8</td>
<td>2</td>
<td>1</td>
<td>5</td>
<td>5</td>
<td>10</td>
<td>1</td>
<td>5</td>
<td>5</td>
<td>10</td>
<td>10</td>
<td>19</td>
<td>1</td>
<td>1</td>
<td>1.0</td>
<td>5.0</td>
<td>8</td>
</tr>
<tr>
<th>8</th>
<th>1</th>
<th>By oft predict that I in heaven find:</th>
<th>1</th>
<th>by OFT pre DICT that I* in HEAV en FIND:</th>
<th>w s w s w s w s w s</th>
<th>0</th>
<th>U P U P U U U P U P</th>
<th>baɪ 'ɔːft prɪ.'dɪkt ðət aɪ ɪn 'hɛ.vən 'faɪnd</th>
<th>0</th>
<th>False</th>
<th></th>
<td>1.0</td>
<td>1.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>4</td>
<td>6</td>
<td>4</td>
<td>2</td>
<td>5</td>
<td>4</td>
<td>10</td>
<td>2</td>
<td>6</td>
<td>5</td>
<td>10</td>
<td>10</td>
<td>19</td>
<td>1</td>
<td>1</td>
<td>2.0</td>
<td>4.0</td>
<td>6</td>
</tr>
<tr>
<th>9</th>
<th>1</th>
<th>But from thine eyes my knowledge I derive,</th>
<th>1</th>
<th>but FROM* thine EYES my KNOWL edge I* de RIVE,</th>
<th>w s w s w s w s w s</th>
<th>0</th>
<th>U U U P U P U U U P</th>
<th>bət frʌm ðaɪn 'aɪz maɪ 'nɑ.ləʤ aɪ dɛː.'aɪv</th>
<th>0</th>
<th>False</th>
<th></th>
<td>2.0</td>
<td>2.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>5</td>
<td>6</td>
<td>4</td>
<td>2</td>
<td>5</td>
<td>3</td>
<td>10</td>
<td>2</td>
<td>7</td>
<td>5</td>
<td>10</td>
<td>10</td>
<td>19</td>
<td>1</td>
<td>1</td>
<td>2.0</td>
<td>3.0</td>
<td>6</td>
</tr>
<tr>
<th>10</th>
<th>1</th>
<th>And constant stars in them I read such art</th>
<th>1</th>
<th>and CON stant STARS in THEM* i READ such ART</th>
<th>w s w s w s w s w s</th>
<th>0</th>
<th>U P U P U U U P U P</th>
<th>ænd 'kɑn.stənt 'stɑrz ɪn ðɛm aɪ 'rɛd səʧ 'ɑrt</th>
<th>0</th>
<th>False</th>
<th></th>
<td>1.0</td>
<td>1.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>5</td>
<td>9</td>
<td>1</td>
<td>1</td>
<td>5</td>
<td>4</td>
<td>10</td>
<td>1</td>
<td>6</td>
<td>5</td>
<td>10</td>
<td>10</td>
<td>19</td>
<td>1</td>
<td>1</td>
<td>1.0</td>
<td>4.0</td>
<td>9</td>
</tr>
<tr>
<th>11</th>
<th>1</th>
<th>As 'truth and beauty shall together thrive,</th>
<th>1</th>
<th>as 'TRUTH and BEAU ty SHALL to GETH er THRIVE,</th>
<th>w s w s w s w s w s</th>
<th>0</th>
<th>U P U P U P U P U P</th>
<th>æz 'truːθ ænd 'bjuː.tiː 'ʃæl tʌ.'gɛ.ðɛː 'θraɪv</th>
<th>0</th>
<th>False</th>
<th></th>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>2</td>
<td>5</td>
<td>5</td>
<td>2</td>
<td>5</td>
<td>5</td>
<td>10</td>
<td>3</td>
<td>5</td>
<td>5</td>
<td>10</td>
<td>10</td>
<td>19</td>
<td>1</td>
<td>1</td>
<td>2.0</td>
<td>5.0</td>
<td>5</td>
</tr>
<tr>
<th>12</th>
<th>1</th>
<th>If from thyself, to store thou wouldst convert';</th>
<th>1</th>
<th>if FROM* thy SELF, to STORE thou WOULDST con VERT';</th>
<th>w s w s w s w s w s</th>
<th>0</th>
<th>U U U P U P U P U P</th>
<th>ɪf frʌm θaɪ.'sɛlf tuː 'stɔːr ðaʊ 'wʊədst kən.'vɛːt</th>
<th>0</th>
<th>False</th>
<th></th>
<td>1.0</td>
<td>1.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>4</td>
<td>7</td>
<td>3</td>
<td>2</td>
<td>5</td>
<td>4</td>
<td>10</td>
<td>2</td>
<td>6</td>
<td>5</td>
<td>10</td>
<td>10</td>
<td>19</td>
<td>1</td>
<td>1</td>
<td>2.0</td>
<td>4.0</td>
<td>7</td>
</tr>
<tr>
<th>13</th>
<th>1</th>
<th>Or else of thee this I prognosticate:</th>
<th>1</th>
<th>or ELSE of THEE* this I* prog* NOS ti CATE:</th>
<th>w s w s w s w s w s</th>
<th>0</th>
<th>U P U U U U S P U S</th>
<th>ɔːr 'ɛls ʌv ðiː ðɪs aɪ `prɑg.'nɑ.stə.`keɪt</th>
<th>0</th>
<th>False</th>
<th></th>
<td>3.0</td>
<td>2.0</td>
<td>0.0</td>
<td>1.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>5</td>
<td>6</td>
<td>4</td>
<td>2</td>
<td>5</td>
<td>4</td>
<td>10</td>
<td>2</td>
<td>6</td>
<td>5</td>
<td>10</td>
<td>10</td>
<td>19</td>
<td>1</td>
<td>1</td>
<td>2.0</td>
<td>3.0</td>
<td>6</td>
</tr>
<tr>
<th>14</th>
<th>1</th>
<th>'Thy end is truth's and beauty's doom and date.'</th>
<th>1</th>
<th>'thy END is TRUTH'S and BEAU ty's DOOM and DATE.'</th>
<th>w s w s w s w s w s</th>
<th>0</th>
<th>U P U P U P U P U P</th>
<th>ðaɪ 'ɛnd ɪz 'truːθs ænd 'bjʉː.tɪz 'duːm ænd 'deɪt</th>
<th>0</th>
<th>False</th>
<th></th>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>4</td>
<td>8</td>
<td>2</td>
<td>1</td>
<td>5</td>
<td>5</td>
<td>10</td>
<td>1</td>
<td>5</td>
<td>5</td>
<td>10</td>
<td>10</td>
<td>19</td>
<td>1</td>
<td>1</td>
<td>1.0</td>
<td>5.0</td>
<td>8</td>
</tr>
</tbody>
</table>
</div>




```python
# any of the above can return syllable level data as well
sonnet.all_parses(by_syll=True)
sonnet.best_parses(by_syll=True)
sonnet.best_parses(by_syll=True).query('line_i==1') # first line
```




<div>

<table border="1" class="dataframe">
<thead>
<tr style="text-align: right;">
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th>*total</th>
<th>*s/unstressed</th>
<th>*w-res</th>
<th>*w/stressed</th>
<th>*clash</th>
<th>*f-res</th>
<th>*w/peak</th>
<th>*lapse</th>
<th>is_funcword</th>
<th>is_heavy</th>
<th>is_light</th>
<th>is_peak</th>
<th>is_s</th>
<th>is_stressed</th>
<th>is_syll</th>
<th>is_trough</th>
<th>is_unstressed</th>
<th>is_w</th>
<th>line_num_syll</th>
<th>parse_num_pos</th>
<th>parse_num_syll</th>
<th>prom_strength</th>
<th>prom_stress</th>
<th>prom_weight</th>
</tr>
<tr>
<th>stanza_i</th>
<th>line_i</th>
<th>linepart_i</th>
<th>line_str</th>
<th>parse_rank</th>
<th>parse_str</th>
<th>parse</th>
<th>parse_i</th>
<th>combo_stress</th>
<th>combo_ipa</th>
<th>combo_i</th>
<th>parse_is_bounded</th>
<th>parse_bounded_by</th>
<th>parse_pos_i</th>
<th>parse_pos</th>
<th>word_i</th>
<th>word_str</th>
<th>word_ipa_i</th>
<th>word_ipa</th>
<th>syll_i</th>
<th>syll_str</th>
<th>syll_ipa</th>
<th>syll_stress</th>
<th>syll_weight</th>
<th>parse_syll_i</th>
<th>parse_syll</th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<th rowspan="10" valign="top">1</th>
<th rowspan="10" valign="top">1</th>
<th rowspan="10" valign="top">1</th>
<th rowspan="10" valign="top">Not from the stars do I my judgement pluck;</th>
<th rowspan="10" valign="top">1</th>
<th rowspan="10" valign="top">not FROM* the STARS do I* my JUDGE ment PLUCK;</th>
<th rowspan="10" valign="top">w s w s w s w s w s</th>
<th rowspan="10" valign="top">1</th>
<th rowspan="10" valign="top">U U U P U U U P U P</th>
<th rowspan="10" valign="top">nɑt frʌm ðə 'stɑrz duː aɪ maɪ 'ʤʌʤ.mənt 'plʌk</th>
<th rowspan="10" valign="top">1</th>
<th rowspan="10" valign="top">False</th>
<th rowspan="10" valign="top"></th>
<th>0</th>
<th>w</th>
<th>1</th>
<th>Not</th>
<th>2</th>
<th>nɑt</th>
<th>1</th>
<th>Not</th>
<th>nɑt</th>
<th>U</th>
<th>H</th>
<th>1</th>
<th>w</th>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>NaN</td>
<td>0.0</td>
<td>0.0</td>
<td>NaN</td>
<td>1</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>0</td>
<td>0</td>
<td>1</td>
<td>0</td>
<td>1</td>
<td>1</td>
<td>10</td>
<td>10</td>
<td>19</td>
<td>NaN</td>
<td>0.0</td>
<td>1</td>
</tr>
<tr>
<th>1</th>
<th>s</th>
<th>2</th>
<th>from</th>
<th>1</th>
<th>frʌm</th>
<th>1</th>
<th>from</th>
<th>frʌm</th>
<th>U</th>
<th>H</th>
<th>1</th>
<th>s</th>
<td>1.0</td>
<td>1.0</td>
<td>0.0</td>
<td>0.0</td>
<td>NaN</td>
<td>0.0</td>
<td>0.0</td>
<td>NaN</td>
<td>1</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>1</td>
<td>0</td>
<td>1</td>
<td>0</td>
<td>1</td>
<td>0</td>
<td>10</td>
<td>10</td>
<td>19</td>
<td>NaN</td>
<td>0.0</td>
<td>1</td>
</tr>
<tr>
<th>2</th>
<th>w</th>
<th>3</th>
<th>the</th>
<th>1</th>
<th>ðə</th>
<th>1</th>
<th>the</th>
<th>ðə</th>
<th>U</th>
<th>L</th>
<th>1</th>
<th>w</th>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>NaN</td>
<td>0.0</td>
<td>0.0</td>
<td>NaN</td>
<td>1</td>
<td>0</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>0</td>
<td>1</td>
<td>0</td>
<td>1</td>
<td>1</td>
<td>10</td>
<td>10</td>
<td>19</td>
<td>NaN</td>
<td>0.0</td>
<td>0</td>
</tr>
<tr>
<th>3</th>
<th>s</th>
<th>4</th>
<th>stars</th>
<th>1</th>
<th>'stɑrz</th>
<th>1</th>
<th>stars</th>
<th>'stɑrz</th>
<th>P</th>
<th>H</th>
<th>1</th>
<th>s</th>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>NaN</td>
<td>0.0</td>
<td>0.0</td>
<td>NaN</td>
<td>0</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>1</td>
<td>1</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>0</td>
<td>10</td>
<td>10</td>
<td>19</td>
<td>NaN</td>
<td>1.0</td>
<td>1</td>
</tr>
<tr>
<th>4</th>
<th>w</th>
<th>5</th>
<th>do</th>
<th>2</th>
<th>duː</th>
<th>1</th>
<th>do</th>
<th>duː</th>
<th>U</th>
<th>L</th>
<th>1</th>
<th>w</th>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>NaN</td>
<td>0.0</td>
<td>0.0</td>
<td>NaN</td>
<td>1</td>
<td>0</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>0</td>
<td>1</td>
<td>0</td>
<td>1</td>
<td>1</td>
<td>10</td>
<td>10</td>
<td>19</td>
<td>NaN</td>
<td>0.0</td>
<td>0</td>
</tr>
<tr>
<th>5</th>
<th>s</th>
<th>6</th>
<th>I</th>
<th>1</th>
<th>aɪ</th>
<th>1</th>
<th>I</th>
<th>aɪ</th>
<th>U</th>
<th>L</th>
<th>1</th>
<th>s</th>
<td>1.0</td>
<td>1.0</td>
<td>0.0</td>
<td>0.0</td>
<td>NaN</td>
<td>0.0</td>
<td>0.0</td>
<td>NaN</td>
<td>1</td>
<td>0</td>
<td>1</td>
<td>0</td>
<td>1</td>
<td>0</td>
<td>1</td>
<td>0</td>
<td>1</td>
<td>0</td>
<td>10</td>
<td>10</td>
<td>19</td>
<td>NaN</td>
<td>0.0</td>
<td>0</td>
</tr>
<tr>
<th>6</th>
<th>w</th>
<th>7</th>
<th>my</th>
<th>1</th>
<th>maɪ</th>
<th>1</th>
<th>my</th>
<th>maɪ</th>
<th>U</th>
<th>L</th>
<th>1</th>
<th>w</th>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>NaN</td>
<td>0.0</td>
<td>0.0</td>
<td>NaN</td>
<td>1</td>
<td>0</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>0</td>
<td>1</td>
<td>0</td>
<td>1</td>
<td>1</td>
<td>10</td>
<td>10</td>
<td>19</td>
<td>NaN</td>
<td>0.0</td>
<td>0</td>
</tr>
<tr>
<th>7</th>
<th>s</th>
<th>8</th>
<th>judgement</th>
<th>1</th>
<th>'ʤʌʤ.mənt</th>
<th>1</th>
<th>judge</th>
<th>'ʤʌʤ</th>
<th>P</th>
<th>H</th>
<th>1</th>
<th>s</th>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>NaN</td>
<td>0.0</td>
<td>0.0</td>
<td>NaN</td>
<td>0</td>
<td>1</td>
<td>0</td>
<td>1</td>
<td>1</td>
<td>1</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>0</td>
<td>10</td>
<td>10</td>
<td>19</td>
<td>1.0</td>
<td>1.0</td>
<td>1</td>
</tr>
<tr>
<th>8</th>
<th>w</th>
<th>8</th>
<th>judgement</th>
<th>1</th>
<th>'ʤʌʤ.mənt</th>
<th>2</th>
<th>ment</th>
<th>mənt</th>
<th>U</th>
<th>H</th>
<th>1</th>
<th>w</th>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>NaN</td>
<td>0.0</td>
<td>0.0</td>
<td>NaN</td>
<td>0</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>0</td>
<td>0</td>
<td>1</td>
<td>1</td>
<td>1</td>
<td>1</td>
<td>10</td>
<td>10</td>
<td>19</td>
<td>0.0</td>
<td>0.0</td>
<td>1</td>
</tr>
<tr>
<th>9</th>
<th>s</th>
<th>9</th>
<th>pluck;</th>
<th>1</th>
<th>'plʌk</th>
<th>1</th>
<th>pluck;</th>
<th>'plʌk</th>
<th>P</th>
<th>H</th>
<th>1</th>
<th>s</th>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>NaN</td>
<td>0.0</td>
<td>0.0</td>
<td>NaN</td>
<td>0</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>1</td>
<td>1</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>0</td>
<td>10</td>
<td>10</td>
<td>19</td>
<td>NaN</td>
<td>1.0</td>
<td>1</td>
</tr>
</tbody>
</table>
</div>




```python
# Best prose parses
para.best_parses()
```




<div>

<table border="1" class="dataframe">
<thead>
<tr style="text-align: right;">
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th>*total</th>
<th>*s/unstressed</th>
<th>*w-res</th>
<th>*w/stressed</th>
<th>*clash</th>
<th>*f-res</th>
<th>*w/peak</th>
<th>*lapse</th>
<th>is_funcword</th>
<th>is_heavy</th>
<th>is_light</th>
<th>is_peak</th>
<th>is_s</th>
<th>is_stressed</th>
<th>is_syll</th>
<th>is_trough</th>
<th>is_unstressed</th>
<th>is_w</th>
<th>line_num_syll</th>
<th>parse_num_pos</th>
<th>parse_num_syll</th>
<th>parse_rank_dense</th>
<th>parse_rank_min</th>
<th>prom_strength</th>
<th>prom_stress</th>
<th>prom_weight</th>
</tr>
<tr>
<th>stanza_i</th>
<th>line_i</th>
<th>linepart_i</th>
<th>line_str</th>
<th>parse_rank</th>
<th>parse_str</th>
<th>parse</th>
<th>parse_i</th>
<th>combo_stress</th>
<th>combo_ipa</th>
<th>combo_i</th>
<th>parse_is_bounded</th>
<th>parse_bounded_by</th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<th rowspan="11" valign="top">1</th>
<th rowspan="3" valign="top">1</th>
<th>1</th>
<th>Is it that by its indefiniteness it shadows forth the heartless voids and immensities of the universe,</th>
<th>1</th>
<th>is.it* THAT by ITS* in DEF i NITE.NESS* it SHAD ows* FORTH the HEART less VOIDS and IM.MEN* si TIES.OF* the UNI ver SE,</th>
<th>w w s w s w s w s s w s w s w s w s w s s w s s w s w s</th>
<th>40</th>
<th>U U P U U U P U U U U P S P U P U P U U P U U U U P U S</th>
<th>ɪz ɪt 'ðæt baɪ ɪts ɪn.'dɛ.fɪ.nʌt.nʌs ɪt 'ʃæ.`doʊz 'fɔːrθ ðə 'hɑrt.ləs 'vɔɪdz ænd ɪ.'mɛn.sɪ.tɪz ʌv ðə 'juː.nʌ.`vɛːs</th>
<th>0</th>
<th>False</th>
<th></th>
<td>16.0</td>
<td>7.0</td>
<td>4.0</td>
<td>1.0</td>
<td>0.0</td>
<td>4.0</td>
<td>0.0</td>
<td>0.0</td>
<td>10</td>
<td>18</td>
<td>10</td>
<td>6</td>
<td>15</td>
<td>10</td>
<td>28</td>
<td>7</td>
<td>18</td>
<td>13</td>
<td>28</td>
<td>24</td>
<td>55</td>
<td>6</td>
<td>66</td>
<td>6.0</td>
<td>9.0</td>
<td>18</td>
</tr>
<tr>
<th>2</th>
<th>and thus stabs us from behind with the thought of annihilation,</th>
<th>1</th>
<th>AND* thus* STABS us FROM* be HIND with THE* thought* OF* an NI hi LA tion,</th>
<th>s w s w s w s w s w s w s w s w</th>
<th>4</th>
<th>U P P U U U P U U P U U S U P U</th>
<th>ænd 'ðʌs 'stæbz əs frʌm bɪ.'haɪnd wɪð ðə 'θɔːt ʌv ə.`naɪ.ə.'leɪ.ʃən</th>
<th>0</th>
<th>False</th>
<th></th>
<td>6.0</td>
<td>4.0</td>
<td>0.0</td>
<td>2.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>6</td>
<td>10</td>
<td>6</td>
<td>3</td>
<td>8</td>
<td>6</td>
<td>16</td>
<td>4</td>
<td>10</td>
<td>8</td>
<td>16</td>
<td>16</td>
<td>31</td>
<td>1</td>
<td>1</td>
<td>3.0</td>
<td>5.5</td>
<td>10</td>
</tr>
<tr>
<th>3</th>
<th>when beholding the white depths of the milky way?</th>
<th>1</th>
<th>WHEN be HOLD ing THE* white* DEPTHS of.the* MI lky WAY?</th>
<th>s w s w s w s w w s w s</th>
<th>0</th>
<th>P U P U U P P U U P U P</th>
<th>'wɛn bɪ.'hoʊl.dɪŋ ðə 'waɪt 'dɛpθs ʌv ðə 'mɪl.kiː 'weɪ</th>
<th>0</th>
<th>False</th>
<th></th>
<td>4.0</td>
<td>1.0</td>
<td>0.0</td>
<td>1.0</td>
<td>0.0</td>
<td>2.0</td>
<td>0.0</td>
<td>0.0</td>
<td>4</td>
<td>7</td>
<td>5</td>
<td>2</td>
<td>6</td>
<td>6</td>
<td>12</td>
<td>3</td>
<td>6</td>
<td>6</td>
<td>12</td>
<td>11</td>
<td>23</td>
<td>1</td>
<td>1</td>
<td>2.0</td>
<td>6.0</td>
<td>7</td>
</tr>
<tr>
<th rowspan="8" valign="top">2</th>
<th>1</th>
<th>Or is it,</th>
<th>1</th>
<th>or IS* it,</th>
<th>w s w</th>
<th>0</th>
<th>U U U</th>
<th>ɔːr ɪz ɪt</th>
<th>0</th>
<th>False</th>
<th></th>
<td>1.0</td>
<td>1.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>3</td>
<td>3</td>
<td>0</td>
<td>0</td>
<td>1</td>
<td>0</td>
<td>3</td>
<td>0</td>
<td>3</td>
<td>2</td>
<td>3</td>
<td>3</td>
<td>5</td>
<td>1</td>
<td>1</td>
<td>0.0</td>
<td>0.0</td>
<td>3</td>
</tr>
<tr>
<th>2</th>
<th>that as in essence whiteness is not so much a colour as the visible absence of colour;</th>
<th>1</th>
<th>that AS* in ESS ence WHITE ness.is* NOT so MUCH a COL our AS* the VIS i BLE* ab* SENCE* of COL our;</th>
<th>w s w s w s w w s w s w s w s w s w s w s w s w</th>
<th>16</th>
<th>U U U P U P U U P U P U P U U U P U U P U U P U</th>
<th>ðət æz ɪn 'ɛ.səns 'waɪt.nəs ɪz 'nɑt soʊ 'mʌʧ eɪ 'kʌ.lʌ æz ðə 'vɪ.zʌ.bəl 'æb.səns ʌv 'kʌ.lʌ</th>
<th>2</th>
<th>False</th>
<th></th>
<td>8.0</td>
<td>4.0</td>
<td>0.0</td>
<td>1.0</td>
<td>0.0</td>
<td>2.0</td>
<td>1.0</td>
<td>0.0</td>
<td>10</td>
<td>14</td>
<td>10</td>
<td>6</td>
<td>11</td>
<td>8</td>
<td>24</td>
<td>6</td>
<td>16</td>
<td>13</td>
<td>24</td>
<td>23</td>
<td>47</td>
<td>1</td>
<td>1</td>
<td>6.0</td>
<td>8.0</td>
<td>14</td>
</tr>
<tr>
<th>3</th>
<th>and at the same time the concrete of all colours;</th>
<th>1</th>
<th>and AT the SAME.TIME* the CON crete OF* all COLO urs;</th>
<th>w s w s s w s w s w s w</th>
<th>0</th>
<th>U P U P P U P U U U P U</th>
<th>ænd 'æt ðə 'seɪm 'taɪm ðə 'kɑn.kriːt ʌv ɔːl 'kʌ.lʌz</th>
<th>0</th>
<th>False</th>
<th></th>
<td>3.0</td>
<td>1.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>2.0</td>
<td>0.0</td>
<td>0.0</td>
<td>7</td>
<td>9</td>
<td>3</td>
<td>2</td>
<td>6</td>
<td>5</td>
<td>12</td>
<td>2</td>
<td>7</td>
<td>6</td>
<td>12</td>
<td>11</td>
<td>23</td>
<td>1</td>
<td>1</td>
<td>2.0</td>
<td>5.0</td>
<td>9</td>
</tr>
<tr>
<th>4</th>
<th>is it for these reasons that there is such a dumb blankness,</th>
<th>1</th>
<th>IS* it FOR* these REA sons THAT there IS* such A* dumb* BLANK ness,</th>
<th>s w s w s w s w s w s w s w</th>
<th>0</th>
<th>U U U U P U P U U U U P P U</th>
<th>ɪz ɪt fɔːr ðiːz 'riː.zənz 'ðæt ðɛr ɪz səʧ eɪ 'dəm 'blæŋk.nʌs</th>
<th>0</th>
<th>False</th>
<th></th>
<td>5.0</td>
<td>4.0</td>
<td>0.0</td>
<td>1.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>9</td>
<td>12</td>
<td>2</td>
<td>2</td>
<td>7</td>
<td>4</td>
<td>14</td>
<td>2</td>
<td>10</td>
<td>7</td>
<td>14</td>
<td>14</td>
<td>27</td>
<td>1</td>
<td>1</td>
<td>2.0</td>
<td>4.0</td>
<td>12</td>
</tr>
<tr>
<th>5</th>
<th>full of meaning,</th>
<th>1</th>
<th>FULL of MEAN ing,</th>
<th>s w s w</th>
<th>0</th>
<th>P U P U</th>
<th>'fʊl ʌv 'miː.nɪŋ</th>
<th>0</th>
<th>False</th>
<th></th>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>1</td>
<td>3</td>
<td>1</td>
<td>1</td>
<td>2</td>
<td>2</td>
<td>4</td>
<td>1</td>
<td>2</td>
<td>2</td>
<td>4</td>
<td>4</td>
<td>7</td>
<td>1</td>
<td>1</td>
<td>1.0</td>
<td>2.0</td>
<td>3</td>
</tr>
<tr>
<th>6</th>
<th>in a wide landscape of snows:</th>
<th>1</th>
<th>IN a WIDE land* SCAPE of SNOWS:</th>
<th>s w s w s w s</th>
<th>0</th>
<th>P U P P S U P</th>
<th>'ɪn eɪ 'waɪd 'lænd.`skeɪp ʌv 'snoʊz</th>
<th>0</th>
<th>False</th>
<th></th>
<td>2.0</td>
<td>0.0</td>
<td>0.0</td>
<td>1.0</td>
<td>0.0</td>
<td>0.0</td>
<td>1.0</td>
<td>0.0</td>
<td>3</td>
<td>6</td>
<td>1</td>
<td>1</td>
<td>4</td>
<td>5</td>
<td>7</td>
<td>1</td>
<td>2</td>
<td>3</td>
<td>7</td>
<td>7</td>
<td>13</td>
<td>1</td>
<td>1</td>
<td>1.0</td>
<td>4.5</td>
<td>6</td>
</tr>
<tr>
<th>7</th>
<th>a colourless,</th>
<th>1</th>
<th>a COLOUR le SS,*</th>
<th>w s w s</th>
<th>0</th>
<th>U P U U</th>
<th>eɪ 'kʌ.lʌ.lʌs</th>
<th>0</th>
<th>False</th>
<th></th>
<td>1.0</td>
<td>1.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>1</td>
<td>1</td>
<td>3</td>
<td>1</td>
<td>2</td>
<td>1</td>
<td>4</td>
<td>1</td>
<td>3</td>
<td>2</td>
<td>4</td>
<td>4</td>
<td>7</td>
<td>1</td>
<td>1</td>
<td>1.0</td>
<td>1.0</td>
<td>1</td>
</tr>
<tr>
<th>8</th>
<th>all-colour of atheism from which we shrink?</th>
<th>1</th>
<th>al L- colour OF* athe I sm.from* WHICH we SHRINK?</th>
<th>w s w s w s w w s w s</th>
<th>0</th>
<th>U P U U U P U U P U P</th>
<th>ɔːl.'kʌ.lʌ ʌv ə.'θaɪ.səm frʌm 'wɪʧ wiː 'ʃrɪŋk</th>
<th>0</th>
<th>False</th>
<th></th>
<td>3.0</td>
<td>1.0</td>
<td>0.0</td>
<td>0.0</td>
<td>0.0</td>
<td>2.0</td>
<td>0.0</td>
<td>0.0</td>
<td>4</td>
<td>6</td>
<td>5</td>
<td>2</td>
<td>5</td>
<td>4</td>
<td>11</td>
<td>4</td>
<td>7</td>
<td>6</td>
<td>12</td>
<td>10</td>
<td>21</td>
<td>1</td>
<td>1</td>
<td>2.0</td>
<td>4.0</td>
<td>6</td>
</tr>
</tbody>
</table>
</div>