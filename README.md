# Cadence

A rhythm analysis toolkit, gathering multiple parsing engines:
* ~~[Prosodic](https://github.com/quadrismegistus/prosodic) for fast English and Finnish metrical scansion.~~
  * Cadence now uses its own metrical parser, a rewritten version of Prosodic's.
* [Stanza](https://github.com/stanfordnlp/stanza) for syntactic parsing.
* [MetricalTree](https://github.com/tdozat/Metrics) for sentence rhythm/phrasal stress assignment based on Stanza's syntactic parses.

## Quickstart

### Install

#### 1. Install python package
```
# install from pypi
pip install -U cadences    # "cadence" was taken :-/

# or from github very latest
pip install -U git+https://github.com/quadrismegistus/cadence
```

#### 2. Insteall espeak (TTS)

Install espeak, free TTS software, to 'sound out' unknown words. See [here](http://espeak.sourceforge.net/download.html) for all downloads.

* On Linux, type into the terminal:
        ```apt-get install espeak```
    
* On Mac:
  * Install [homebrew](brew.sh) if not already installed.

  * Type into the Terminal app: `brew install espeak`
    
* On Windows:
        Download and install from http://espeak.sourceforge.net/download.html.

### Load cadence

```python
# this should work following installation
import cadence as cd
```

### Load texts

```python
# verse
sonnetXIV = """
How can I then return in happy plight,
That am debarred the benefit of rest?
When day’s oppression is not eased by night,
But day by night and night by day oppressed,
And each, though enemies to either’s reign,
Do in consent shake hands to torture me,
The one by toil, the other to complain
How far I toil, still farther off from thee.
I tell the day, to please him thou art bright,
And dost him grace when clouds do blot the heaven:
So flatter I the swart-complexiond night,
When sparkling stars twire not thou gildst the even.
But day doth daily draw my sorrows longer,
And night doth nightly make grief’s length seem stronger.
"""

# prose
melville="""Is it that by its indefiniteness it shadows forth the
heartless voids and immensities of the universe, and thus stabs us
from behind with the thought of annihilation, when beholding
the white depths of the milky way? Or is it, that as in
essence whiteness is not so much a colour as the visible absence
of colour; and at the same time the concrete of all colours;
is it for these reasons that there is such a dumb blankness,
full of meaning, in a wide landscape of snows: a colourless,
all-colour of atheism from which we shrink?"""
```


```python
# These are identical
sonnet = cd.Verse(sonnetXIV)
sonnet = cd.Text(sonnetXIV, linebreaks=True, phrasebreaks=False)

# So are these
prose = cd.Prose(melville)
prose = cd.Text(melville, linebreaks=False, phrasebreaks=True)
```

### Available features

```python
# Tokenize
sonnet.words()
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
      <th>word_ispunc</th>
    </tr>
    <tr>
      <th>para_i</th>
      <th>sent_i</th>
      <th>sentpart_i</th>
      <th>line_i</th>
      <th>word_i</th>
      <th>word_str</th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="11" valign="top">1</th>
      <th rowspan="5" valign="top">1</th>
      <th rowspan="5" valign="top">1</th>
      <th rowspan="5" valign="top">1</th>
      <th>1</th>
      <th>How</th>
      <td>0</td>
    </tr>
    <tr>
      <th>2</th>
      <th>can</th>
      <td>0</td>
    </tr>
    <tr>
      <th>3</th>
      <th>I</th>
      <td>0</td>
    </tr>
    <tr>
      <th>4</th>
      <th>then</th>
      <td>0</td>
    </tr>
    <tr>
      <th>5</th>
      <th>return</th>
      <td>0</td>
    </tr>
    <tr>
      <th>...</th>
      <th>...</th>
      <th>...</th>
      <th>...</th>
      <th>...</th>
      <td>...</td>
    </tr>
    <tr>
      <th rowspan="5" valign="top">4</th>
      <th rowspan="5" valign="top">17</th>
      <th rowspan="5" valign="top">14</th>
      <th>15</th>
      <th>grief's</th>
      <td>0</td>
    </tr>
    <tr>
      <th>16</th>
      <th>length</th>
      <td>0</td>
    </tr>
    <tr>
      <th>17</th>
      <th>seem</th>
      <td>0</td>
    </tr>
    <tr>
      <th>18</th>
      <th>stronger</th>
      <td>0</td>
    </tr>
    <tr>
      <th>19</th>
      <th>.</th>
      <td>1</td>
    </tr>
  </tbody>
</table>
<p>135 rows × 1 columns</p>
</div>




```python
# Syllabify
sonnet.sylls()
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
      <th>prom_strength</th>
      <th>prom_stress</th>
      <th>prom_weight</th>
      <th>word_isfunc</th>
      <th>word_ispunc</th>
      <th>word_nsyll</th>
    </tr>
    <tr>
      <th>para_i</th>
      <th>sent_i</th>
      <th>sentpart_i</th>
      <th>line_i</th>
      <th>word_i</th>
      <th>word_str</th>
      <th>word_tok</th>
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
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="11" valign="top">1</th>
      <th rowspan="5" valign="top">1</th>
      <th rowspan="5" valign="top">1</th>
      <th rowspan="5" valign="top">1</th>
      <th>1</th>
      <th>How</th>
      <th>how</th>
      <th>1</th>
      <th>haʊ</th>
      <th>1</th>
      <th>How</th>
      <th>haʊ</th>
      <th>U</th>
      <th>H</th>
      <td>NaN</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>1.0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2</th>
      <th>can</th>
      <th>can</th>
      <th>1</th>
      <th>kæn</th>
      <th>1</th>
      <th>can</th>
      <th>kæn</th>
      <th>U</th>
      <th>H</th>
      <td>NaN</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>1.0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">3</th>
      <th rowspan="2" valign="top">I</th>
      <th rowspan="2" valign="top">i</th>
      <th>1</th>
      <th>'aɪ</th>
      <th>1</th>
      <th>I</th>
      <th>'aɪ</th>
      <th>P</th>
      <th>H</th>
      <td>1.0</td>
      <td>1.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2</th>
      <th>aɪ</th>
      <th>1</th>
      <th>I</th>
      <th>aɪ</th>
      <th>U</th>
      <th>H</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>1.0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>4</th>
      <th>then</th>
      <th>then</th>
      <th>1</th>
      <th>'ðɛn</th>
      <th>1</th>
      <th>then</th>
      <th>'ðɛn</th>
      <th>P</th>
      <th>H</th>
      <td>1.0</td>
      <td>1.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0</td>
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
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th rowspan="5" valign="top">4</th>
      <th rowspan="5" valign="top">17</th>
      <th rowspan="5" valign="top">14</th>
      <th>16</th>
      <th>length</th>
      <th>length</th>
      <th>1</th>
      <th>'lɛŋkθ</th>
      <th>1</th>
      <th>length</th>
      <th>'lɛŋkθ</th>
      <th>P</th>
      <th>H</th>
      <td>NaN</td>
      <td>1.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>17</th>
      <th>seem</th>
      <th>seem</th>
      <th>1</th>
      <th>'siːm</th>
      <th>1</th>
      <th>seem</th>
      <th>'siːm</th>
      <th>P</th>
      <th>H</th>
      <td>NaN</td>
      <td>1.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">18</th>
      <th rowspan="2" valign="top">stronger</th>
      <th rowspan="2" valign="top">stronger</th>
      <th rowspan="2" valign="top">1</th>
      <th rowspan="2" valign="top">'strɔːŋ.ɛː</th>
      <th>1</th>
      <th>stron</th>
      <th>'strɔːŋ</th>
      <th>P</th>
      <th>H</th>
      <td>1.0</td>
      <td>1.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2</th>
      <th>ger</th>
      <th>ɛː</th>
      <th>U</th>
      <th>L</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0</td>
      <td>2</td>
    </tr>
    <tr>
      <th>19</th>
      <th>.</th>
      <th></th>
      <th>0</th>
      <th></th>
      <th>0</th>
      <th>.</th>
      <th></th>
      <th>NaN</th>
      <th>NaN</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>1</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
<p>186 rows × 6 columns</p>
</div>




```python
# Syntax-parse
sonnet.syntax()
```




<div>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th>dep_head</th>
      <th>dep_type</th>
      <th>pos_case</th>
      <th>pos_definite</th>
      <th>pos_degree</th>
      <th>pos_gender</th>
      <th>pos_mood</th>
      <th>pos_number</th>
      <th>pos_person</th>
      <th>pos_polarity</th>
      <th>pos_poss</th>
      <th>pos_prontype</th>
      <th>pos_tense</th>
      <th>pos_upos</th>
      <th>pos_verbform</th>
      <th>pos_voice</th>
      <th>pos_xpos</th>
      <th>word_depth</th>
    </tr>
    <tr>
      <th>para_i</th>
      <th>sent_i</th>
      <th>word_i</th>
      <th>word_str</th>
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
      <th rowspan="5" valign="top">1</th>
      <th>1</th>
      <th>How</th>
      <td>5</td>
      <td>advmod</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>Int</td>
      <td></td>
      <td>ADV</td>
      <td></td>
      <td></td>
      <td>WRB</td>
      <td>4</td>
    </tr>
    <tr>
      <th>2</th>
      <th>can</th>
      <td>5</td>
      <td>aux</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>AUX</td>
      <td>Fin</td>
      <td></td>
      <td>MD</td>
      <td>4</td>
    </tr>
    <tr>
      <th>3</th>
      <th>I</th>
      <td>5</td>
      <td>nsubj</td>
      <td>Nom</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>Sing</td>
      <td>1</td>
      <td></td>
      <td></td>
      <td>Prs</td>
      <td></td>
      <td>PRON</td>
      <td></td>
      <td></td>
      <td>PRP</td>
      <td>5</td>
    </tr>
    <tr>
      <th>4</th>
      <th>then</th>
      <td>5</td>
      <td>advmod</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>Dem</td>
      <td></td>
      <td>ADV</td>
      <td></td>
      <td></td>
      <td>RB</td>
      <td>5</td>
    </tr>
    <tr>
      <th>5</th>
      <th>return</th>
      <td>0</td>
      <td>root</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>VERB</td>
      <td>Inf</td>
      <td></td>
      <td>VB</td>
      <td>5</td>
    </tr>
    <tr>
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
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th rowspan="5" valign="top">4</th>
      <th>15</th>
      <th>grief's</th>
      <td>16</td>
      <td>compound</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>Plur</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>NOUN</td>
      <td></td>
      <td></td>
      <td>NNS</td>
      <td>8</td>
    </tr>
    <tr>
      <th>16</th>
      <th>length</th>
      <td>14</td>
      <td>obj</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>Sing</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>NOUN</td>
      <td></td>
      <td></td>
      <td>NN</td>
      <td>8</td>
    </tr>
    <tr>
      <th>17</th>
      <th>seem</th>
      <td>14</td>
      <td>xcomp</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>VERB</td>
      <td>Inf</td>
      <td></td>
      <td>VB</td>
      <td>10</td>
    </tr>
    <tr>
      <th>18</th>
      <th>stronger</th>
      <td>17</td>
      <td>xcomp</td>
      <td></td>
      <td></td>
      <td>Cmp</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>ADJ</td>
      <td></td>
      <td></td>
      <td>JJR</td>
      <td>12</td>
    </tr>
    <tr>
      <th>19</th>
      <th>.</th>
      <td>5</td>
      <td>punct</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>PUNCT</td>
      <td></td>
      <td></td>
      <td>.</td>
      <td>3</td>
    </tr>
  </tbody>
</table>
<p>135 rows × 18 columns</p>
</div>


### Sentence-level information from MetricalTree


```python
# Show sentences
sentence = sonnet.sent(1)
sentence.mtree()
```

![svg](README_files/README_10_0.svg)
    
```python
# Show sentence tree for prose
prose.sent(1).mtree()
```

    
![svg](README_files/README_17_0.svg)
    





```python
# Stress grid of sentence inferred from syntactic tree
sentence.grid()
```


    
![png](README_files/README_11_0.png)
    

### Metrical parsing

```python
# Parse lines (verse)
sonnet.parse()
```


 How can <i><b>I</b></i> <i><b>then</b></i> re<i><b>turn</b></i> in <i><b>hap</b></i>py <i><b>plight</b></i>,



 That <i>am</i> de<i><b>barred</b></i> the <i><b>be</b></i>ne<i>fit</i> of <i><b>rest</b></i>?



 When <i><b>day's</b></i> op<i><b>pres</b></i>sion <i><b>is</b></i> not <i><b>eased</b></i> by <i><b>night</b></i>,



 But <i><b>day</b></i> by <i><b>night</b></i> and <i><b>night</b></i> by <i><b>day</b></i> op<i><b>pressed</b></i>,



 And <i><b>each</b></i>, though <i><b>e</b></i>ne<i>mies</i> to <i><b>eit</b></i>her's <i><b>reign</b></i>,



 Do <i><b>in</b></i> con<i><b>sent</b></i> <b>shake</b> <i><b>hands</b></i> to <i><b>tor</b></i>ture <i>me</i>,



 The <i>one</i> by <i><b>toil</b></i>, the <i><b>ot</b></i>her <i>to</i> com<i><b>plain</b></i>



 How <i><b>far</b></i> I <i><b>toil</b></i>, <b>still</b> <i><b>fart</b></i>her <i>off</i> from thee.



 I <i><b>tell</b></i> the <i><b>day</b></i>, to <i><b>please</b></i> him thou <i><b>art</b></i> <b>bright</b>,



 And <i><b>dost</b></i> him <i><b>grace</b></i> when <i><b>clouds</b></i> do <i><b>blot</b></i> the <i><b>heaven</b></i>:



 So <i><b>flat</b></i>ter <i><b>I</b></i> the <i><b>swart</b></i>- com<i><b>ple</b></i>xiond <i><b>night</b></i>,



 When <i><b>spar</b></i>kling <i><b>stars</b></i> <i><b>twi</b></i>re <i><b>not</b></i> thou <i><b>gildst</b></i> the <i><b>e</b></i>ven.



 But <i><b>day</b></i> doth <i><b>dai</b></i>ly <i><b>draw</b></i> my <i><b>sor</b></i>rows <i><b>lon</b></i>ger,



 And <i><b>night</b></i> doth <i><b>nigh</b></i>tly <i><b>make</b></i> <b>grief's</b> <i><b>length</b></i> <b>seem</b> <i><b>stron</b></i>ger.





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
      <th>*total</th>
      <th>*s_unstressed</th>
      <th>*unres_across</th>
      <th>*unres_within</th>
      <th>*w_peak</th>
      <th>*w_stressed</th>
      <th>dep_head</th>
      <th>dep_type</th>
      <th>mtree_ishead</th>
      <th>num_parses</th>
      <th>pos_case</th>
      <th>pos_definite</th>
      <th>pos_degree</th>
      <th>pos_gender</th>
      <th>pos_mood</th>
      <th>pos_number</th>
      <th>pos_person</th>
      <th>pos_polarity</th>
      <th>pos_poss</th>
      <th>pos_prontype</th>
      <th>pos_tense</th>
      <th>pos_upos</th>
      <th>pos_verbform</th>
      <th>pos_voice</th>
      <th>pos_xpos</th>
      <th>prom_lstress</th>
      <th>prom_pstrength</th>
      <th>prom_pstress</th>
      <th>prom_strength</th>
      <th>prom_stress</th>
      <th>prom_tstress</th>
      <th>prom_weight</th>
      <th>word_depth</th>
      <th>word_isfunc</th>
      <th>word_ispunc</th>
      <th>word_nsyll</th>
    </tr>
    <tr>
      <th>para_i</th>
      <th>unit_i</th>
      <th>parse_rank</th>
      <th>is_troch</th>
      <th>parse_i</th>
      <th>parse</th>
      <th>parse_str</th>
      <th>sent_i</th>
      <th>sentpart_i</th>
      <th>line_i</th>
      <th>combo_i</th>
      <th>slot_i</th>
      <th>slot_meter</th>
      <th>syll_str_parse</th>
      <th>word_i</th>
      <th>word_str</th>
      <th>word_tok</th>
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
      <th rowspan="5" valign="top">1</th>
      <th rowspan="5" valign="top">1</th>
      <th rowspan="5" valign="top">0</th>
      <th rowspan="5" valign="top">1</th>
      <th rowspan="5" valign="top">wwSSwSwSwS</th>
      <th rowspan="5" valign="top">𝖧𝗈𝗐 𝖼𝖺𝗇 𝗜 𝙩𝙝𝙚𝙣 𝗋𝖾𝘁𝘂𝗿𝗻 𝗂𝗇 𝗵𝗮𝗽𝗉𝗒 𝗽𝗹𝗶𝗴𝗵𝘁,</th>
      <th rowspan="5" valign="top">1</th>
      <th rowspan="5" valign="top">1</th>
      <th rowspan="5" valign="top">1</th>
      <th rowspan="5" valign="top">1</th>
      <th>1</th>
      <th>w</th>
      <th>𝖧𝗈𝗐</th>
      <th>1</th>
      <th>How</th>
      <th>how</th>
      <th>1</th>
      <th>haʊ</th>
      <th>1</th>
      <th>How</th>
      <th>haʊ</th>
      <th>U</th>
      <th>H</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>5</td>
      <td>advmod</td>
      <td>NaN</td>
      <td>4</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>Int</td>
      <td></td>
      <td>ADV</td>
      <td></td>
      <td></td>
      <td>WRB</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>0.000000</td>
      <td>1.0</td>
      <td>4</td>
      <td>1.0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2</th>
      <th>w</th>
      <th>𝖼𝖺𝗇</th>
      <th>2</th>
      <th>can</th>
      <th>can</th>
      <th>1</th>
      <th>kæn</th>
      <th>1</th>
      <th>can</th>
      <th>kæn</th>
      <th>U</th>
      <th>H</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>5</td>
      <td>aux</td>
      <td>NaN</td>
      <td>4</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>AUX</td>
      <td>Fin</td>
      <td></td>
      <td>MD</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>0.333333</td>
      <td>1.0</td>
      <td>4</td>
      <td>1.0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>3</th>
      <th>s</th>
      <th>𝗜</th>
      <th>3</th>
      <th>I</th>
      <th>i</th>
      <th>1</th>
      <th>'aɪ</th>
      <th>1</th>
      <th>I</th>
      <th>'aɪ</th>
      <th>P</th>
      <th>H</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>5</td>
      <td>nsubj</td>
      <td>NaN</td>
      <td>4</td>
      <td>Nom</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>Sing</td>
      <td>1</td>
      <td></td>
      <td></td>
      <td>Prs</td>
      <td></td>
      <td>PRON</td>
      <td></td>
      <td></td>
      <td>PRP</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>1.0</td>
      <td>0.000000</td>
      <td>1.0</td>
      <td>5</td>
      <td>0.0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>4</th>
      <th>s</th>
      <th>𝙩𝙝𝙚𝙣</th>
      <th>4</th>
      <th>then</th>
      <th>then</th>
      <th>1</th>
      <th>'ðɛn</th>
      <th>1</th>
      <th>then</th>
      <th>'ðɛn</th>
      <th>P</th>
      <th>H</th>
      <td>1.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>5</td>
      <td>advmod</td>
      <td>NaN</td>
      <td>4</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>Dem</td>
      <td></td>
      <td>ADV</td>
      <td></td>
      <td></td>
      <td>RB</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>1.0</td>
      <td>0.000000</td>
      <td>1.0</td>
      <td>5</td>
      <td>0.0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>5</th>
      <th>w</th>
      <th>𝗋𝖾</th>
      <th>5</th>
      <th>return</th>
      <th>return</th>
      <th>1</th>
      <th>rɪ.'tɛːn</th>
      <th>1</th>
      <th>re</th>
      <th>rɪ</th>
      <th>U</th>
      <th>L</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0</td>
      <td>root</td>
      <td>NaN</td>
      <td>4</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>VERB</td>
      <td>Inf</td>
      <td></td>
      <td>VB</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>5</td>
      <td>0.0</td>
      <td>0</td>
      <td>2</td>
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
      <th rowspan="5" valign="top">2</th>
      <th rowspan="5" valign="top">0</th>
      <th rowspan="5" valign="top">1</th>
      <th rowspan="5" valign="top">wSwSwSSwSSw</th>
      <th rowspan="5" valign="top">𝖠𝗇𝖽 𝗻𝗶𝗴𝗵𝘁 𝖽𝗈𝗍𝗁 𝗻𝗶𝗴𝗵𝗍𝗅𝗒 𝗺𝗮𝗸𝗲 𝙜𝙧𝙞𝙚𝙛'𝙨 𝘭𝘦𝘯𝘨𝘵𝘩 𝘀𝗲𝗲𝗺 𝙨𝙩𝙧𝙤𝙣𝗀𝖾𝗋.</th>
      <th rowspan="5" valign="top">4</th>
      <th rowspan="5" valign="top">17</th>
      <th rowspan="5" valign="top">14</th>
      <th rowspan="5" valign="top">1</th>
      <th>8</th>
      <th>w</th>
      <th>𝘭𝘦𝘯𝘨𝘵𝘩</th>
      <th>16</th>
      <th>length</th>
      <th>length</th>
      <th>1</th>
      <th>'lɛŋkθ</th>
      <th>1</th>
      <th>length</th>
      <th>'lɛŋkθ</th>
      <th>P</th>
      <th>H</th>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>14</td>
      <td>obj</td>
      <td>NaN</td>
      <td>2</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>Sing</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>NOUN</td>
      <td></td>
      <td></td>
      <td>NN</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>1.0</td>
      <td>0.750000</td>
      <td>1.0</td>
      <td>8</td>
      <td>0.0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>9</th>
      <th>s</th>
      <th>𝘀𝗲𝗲𝗺</th>
      <th>17</th>
      <th>seem</th>
      <th>seem</th>
      <th>1</th>
      <th>'siːm</th>
      <th>1</th>
      <th>seem</th>
      <th>'siːm</th>
      <th>P</th>
      <th>H</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>14</td>
      <td>xcomp</td>
      <td>NaN</td>
      <td>2</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>VERB</td>
      <td>Inf</td>
      <td></td>
      <td>VB</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>1.0</td>
      <td>0.750000</td>
      <td>1.0</td>
      <td>10</td>
      <td>0.0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>10</th>
      <th>s</th>
      <th>𝙨𝙩𝙧𝙤𝙣</th>
      <th>18</th>
      <th>stronger</th>
      <th>stronger</th>
      <th>1</th>
      <th>'strɔːŋ.ɛː</th>
      <th>1</th>
      <th>stron</th>
      <th>'strɔːŋ</th>
      <th>P</th>
      <th>H</th>
      <td>1.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>17</td>
      <td>xcomp</td>
      <td>NaN</td>
      <td>2</td>
      <td></td>
      <td></td>
      <td>Cmp</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>ADJ</td>
      <td></td>
      <td></td>
      <td>JJR</td>
      <td>1.0</td>
      <td>1.0</td>
      <td>1.0</td>
      <td>1.0</td>
      <td>1.0</td>
      <td>1.000000</td>
      <td>1.0</td>
      <td>12</td>
      <td>0.0</td>
      <td>0</td>
      <td>2</td>
    </tr>
    <tr>
      <th>11</th>
      <th>w</th>
      <th>𝗀𝖾𝗋</th>
      <th>18</th>
      <th>stronger</th>
      <th>stronger</th>
      <th>1</th>
      <th>'strɔːŋ.ɛː</th>
      <th>2</th>
      <th>ger</th>
      <th>ɛː</th>
      <th>U</th>
      <th>L</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>17</td>
      <td>xcomp</td>
      <td>NaN</td>
      <td>2</td>
      <td></td>
      <td></td>
      <td>Cmp</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>ADJ</td>
      <td></td>
      <td></td>
      <td>JJR</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>12</td>
      <td>0.0</td>
      <td>0</td>
      <td>2</td>
    </tr>
    <tr>
      <th>12</th>
      <th>NaN</th>
      <th>.</th>
      <th>19</th>
      <th>.</th>
      <th></th>
      <th>0</th>
      <th></th>
      <th>0</th>
      <th>.</th>
      <th></th>
      <th>NaN</th>
      <th>NaN</th>
      <td>0.0</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>5</td>
      <td>punct</td>
      <td>NaN</td>
      <td>2</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>PUNCT</td>
      <td></td>
      <td></td>
      <td>.</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>3</td>
      <td>NaN</td>
      <td>1</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
<p>303 rows × 36 columns</p>
</div>



```python
# Parse prose
prose.parse()
```



 Is <i><b>it</b></i> that by <i>its</i> in<i><b>de</b></i>fi<i>ni</i>teness it <i><b>sha</b></i><i><b>dows</b></i> <b>forth</b>



 the <i><b>hear</b></i>tless <i><b>voids</b></i> and im<i><b>men</b></i>si<i>ties</i> of the <i><b>u</b></i>ni<i><b>verse</b></i>,



 and <i><b>thus</b></i>



 <i><b>stabs</b></i> us <i>from</i> be<i><b>hind</b></i> with the <i><b>thought</b></i> of an<i><b>ni</b></i>hi<i><b>la</b></i>tion,



 <i><b>when</b></i> be<i><b>hol</b></i>ding the <i><b>white</b></i> <i><b>depths</b></i> of the <i><b>mil</b></i>ky <i><b>way</b></i>?



 Or <i><b>is</b></i> it,



 <i><b>that</b></i> as in <i><b>es</b></i>sence <i><b>whi</b></i>teness <i><b>is</b></i> not so



 much a <i><b>co</b></i>lour <i>as</i> the <i><b>vi</b></i>sible <i><b>a</b></i>bsence of <i><b>co</b></i>lour;



 and <i><b>at</b></i> the <i><b>same</b></i> <i><b>time</b></i> the <i><b>con</b></i>crete <i>of</i> all <i><b>co</b></i>lours;



 is <i><b>it</b></i> for these <i><b>rea</b></i>sons <i><b>that</b></i> there <i><b>is</b></i> such a <i><b>dumb</b></i> <i><b>blan</b></i>kness,



 <i><b>full</b></i> of <i><b>mea</b></i>ning,



 in a <i><b>wide</b></i> <b>lands</b><i><b>cape</b></i> of <i><b>snows</b></i>:



 a <i><b>co</b></i>lourless,



 all- <i><b>co</b></i>lour <i>of</i> at<i><b>he</b></i>ism from <i><b>which</b></i> we <i><b>shrink</b></i>?





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
      <th>*total</th>
      <th>*s_unstressed</th>
      <th>*unres_across</th>
      <th>*unres_within</th>
      <th>*w_peak</th>
      <th>*w_stressed</th>
      <th>dep_head</th>
      <th>dep_type</th>
      <th>mtree_ishead</th>
      <th>num_parses</th>
      <th>pos_case</th>
      <th>pos_definite</th>
      <th>pos_degree</th>
      <th>pos_gender</th>
      <th>pos_mood</th>
      <th>pos_number</th>
      <th>pos_person</th>
      <th>pos_polarity</th>
      <th>pos_poss</th>
      <th>pos_prontype</th>
      <th>pos_tense</th>
      <th>pos_upos</th>
      <th>pos_verbform</th>
      <th>pos_xpos</th>
      <th>prom_lstress</th>
      <th>prom_pstrength</th>
      <th>prom_pstress</th>
      <th>prom_strength</th>
      <th>prom_stress</th>
      <th>prom_tstress</th>
      <th>prom_weight</th>
      <th>word_depth</th>
      <th>word_isfunc</th>
      <th>word_ispunc</th>
      <th>word_nsyll</th>
    </tr>
    <tr>
      <th>para_i</th>
      <th>unit_i</th>
      <th>parse_rank</th>
      <th>is_troch</th>
      <th>parse_i</th>
      <th>parse</th>
      <th>parse_str</th>
      <th>sent_i</th>
      <th>sentpart_i</th>
      <th>line_i</th>
      <th>combo_i</th>
      <th>slot_i</th>
      <th>slot_meter</th>
      <th>syll_str_parse</th>
      <th>word_i</th>
      <th>word_str</th>
      <th>word_tok</th>
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
      <th rowspan="5" valign="top">1</th>
      <th rowspan="5" valign="top">1</th>
      <th rowspan="5" valign="top">0</th>
      <th rowspan="5" valign="top">1</th>
      <th rowspan="5" valign="top">wSwwSwSwSwwSSw</th>
      <th rowspan="5" valign="top">𝖨𝗌 𝗶𝘁 𝗍𝗁𝖺𝗍 𝖻𝗒 𝙞𝙩𝙨 𝗂𝗇𝗱𝗲𝖿𝗂𝙣𝙞𝗍𝖾𝗇𝖾𝗌𝗌 𝘪𝘵 𝘀𝗵𝗮𝗱𝗼𝘄𝘀 𝘧𝘰𝘳𝘵𝘩</th>
      <th rowspan="5" valign="top">1</th>
      <th rowspan="5" valign="top">1</th>
      <th rowspan="5" valign="top">1</th>
      <th rowspan="5" valign="top">12</th>
      <th>1</th>
      <th>w</th>
      <th>𝖨𝗌</th>
      <th>1</th>
      <th>Is</th>
      <th>is</th>
      <th>2</th>
      <th>ɪz</th>
      <th>1</th>
      <th>Is</th>
      <th>ɪz</th>
      <th>U</th>
      <th>H</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>8</td>
      <td>aux</td>
      <td>0.0</td>
      <td>27</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>Ind</td>
      <td>Sing</td>
      <td>3</td>
      <td></td>
      <td></td>
      <td></td>
      <td>Pres</td>
      <td>AUX</td>
      <td>Fin</td>
      <td>VBZ</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.666667</td>
      <td>1.0</td>
      <td>3</td>
      <td>1.0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2</th>
      <th>s</th>
      <th>𝗶𝘁</th>
      <th>2</th>
      <th>it</th>
      <th>it</th>
      <th>1</th>
      <th>'ɪt</th>
      <th>1</th>
      <th>it</th>
      <th>'ɪt</th>
      <th>P</th>
      <th>H</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>8</td>
      <td>nsubj</td>
      <td>NaN</td>
      <td>27</td>
      <td>Nom</td>
      <td></td>
      <td></td>
      <td>Neut</td>
      <td></td>
      <td>Sing</td>
      <td>3</td>
      <td></td>
      <td></td>
      <td>Prs</td>
      <td></td>
      <td>PRON</td>
      <td></td>
      <td>PRP</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>1.0</td>
      <td>0.333333</td>
      <td>1.0</td>
      <td>4</td>
      <td>0.0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>3</th>
      <th>w</th>
      <th>𝗍𝗁𝖺𝗍</th>
      <th>3</th>
      <th>that</th>
      <th>that</th>
      <th>2</th>
      <th>ðət</th>
      <th>1</th>
      <th>that</th>
      <th>ðət</th>
      <th>U</th>
      <th>H</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>8</td>
      <td>mark</td>
      <td>NaN</td>
      <td>27</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>SCONJ</td>
      <td></td>
      <td>IN</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.333333</td>
      <td>1.0</td>
      <td>4</td>
      <td>1.0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>4</th>
      <th>w</th>
      <th>𝖻𝗒</th>
      <th>4</th>
      <th>by</th>
      <th>by</th>
      <th>1</th>
      <th>baɪ</th>
      <th>1</th>
      <th>by</th>
      <th>baɪ</th>
      <th>U</th>
      <th>H</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>6</td>
      <td>case</td>
      <td>NaN</td>
      <td>27</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>ADP</td>
      <td></td>
      <td>IN</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>0.333333</td>
      <td>1.0</td>
      <td>4</td>
      <td>1.0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>5</th>
      <th>s</th>
      <th>𝙞𝙩𝙨</th>
      <th>5</th>
      <th>its</th>
      <th>its</th>
      <th>1</th>
      <th>ɪts</th>
      <th>1</th>
      <th>its</th>
      <th>ɪts</th>
      <th>U</th>
      <th>H</th>
      <td>1.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>6</td>
      <td>nmod:poss</td>
      <td>0.0</td>
      <td>27</td>
      <td></td>
      <td></td>
      <td></td>
      <td>Neut</td>
      <td></td>
      <td>Sing</td>
      <td>3</td>
      <td></td>
      <td>Yes</td>
      <td>Prs</td>
      <td></td>
      <td>PRON</td>
      <td></td>
      <td>PRP$</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>0.333333</td>
      <td>1.0</td>
      <td>5</td>
      <td>1.0</td>
      <td>0</td>
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
      <th rowspan="5" valign="top">8</th>
      <th rowspan="5" valign="top">0</th>
      <th rowspan="5" valign="top">8</th>
      <th rowspan="5" valign="top">wSwwSwSwwSwS</th>
      <th rowspan="5" valign="top">𝖺𝗅𝗅- 𝗰𝗼𝗅𝗈𝗎𝗋 𝘰𝘧 𝗮𝘁𝗁𝖾𝗶𝗌𝗆 𝘧𝘳𝘰𝘮 𝘄𝗵𝗶𝗰𝗵 𝗐𝖾 𝘀𝗵𝗿𝗶𝗻𝗸?</th>
      <th rowspan="5" valign="top">2</th>
      <th rowspan="5" valign="top">11</th>
      <th rowspan="5" valign="top">6</th>
      <th rowspan="5" valign="top">14</th>
      <th>10</th>
      <th>w</th>
      <th>𝘧𝘳𝘰𝘮</th>
      <th>66</th>
      <th>from</th>
      <th>from</th>
      <th>1</th>
      <th>frʌm</th>
      <th>1</th>
      <th>from</th>
      <th>frʌm</th>
      <th>U</th>
      <th>H</th>
      <td>1.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>67</td>
      <td>case</td>
      <td>NaN</td>
      <td>8</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>ADP</td>
      <td></td>
      <td>IN</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>0.250000</td>
      <td>1.0</td>
      <td>13</td>
      <td>1.0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>11</th>
      <th>s</th>
      <th>𝘄𝗵𝗶𝗰𝗵</th>
      <th>67</th>
      <th>which</th>
      <th>which</th>
      <th>1</th>
      <th>'wɪʧ</th>
      <th>1</th>
      <th>which</th>
      <th>'wɪʧ</th>
      <th>P</th>
      <th>H</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>69</td>
      <td>obl</td>
      <td>NaN</td>
      <td>8</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>Rel</td>
      <td></td>
      <td>PRON</td>
      <td></td>
      <td>WDT</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>1.0</td>
      <td>0.000000</td>
      <td>1.0</td>
      <td>14</td>
      <td>0.0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>12</th>
      <th>w</th>
      <th>𝗐𝖾</th>
      <th>68</th>
      <th>we</th>
      <th>we</th>
      <th>2</th>
      <th>wiː</th>
      <th>1</th>
      <th>we</th>
      <th>wiː</th>
      <th>U</th>
      <th>L</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>69</td>
      <td>nsubj</td>
      <td>NaN</td>
      <td>8</td>
      <td>Nom</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>Plur</td>
      <td>1</td>
      <td></td>
      <td></td>
      <td>Prs</td>
      <td></td>
      <td>PRON</td>
      <td></td>
      <td>PRP</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.250000</td>
      <td>0.0</td>
      <td>14</td>
      <td>1.0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>13</th>
      <th>s</th>
      <th>𝘀𝗵𝗿𝗶𝗻𝗸</th>
      <th>69</th>
      <th>shrink</th>
      <th>shrink</th>
      <th>1</th>
      <th>'ʃrɪŋk</th>
      <th>1</th>
      <th>shrink</th>
      <th>'ʃrɪŋk</th>
      <th>P</th>
      <th>H</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>63</td>
      <td>acl:relcl</td>
      <td>NaN</td>
      <td>8</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>Ind</td>
      <td>Plur</td>
      <td>1</td>
      <td></td>
      <td></td>
      <td></td>
      <td>Pres</td>
      <td>VERB</td>
      <td>Fin</td>
      <td>VBP</td>
      <td>1.0</td>
      <td>1.0</td>
      <td>1.0</td>
      <td>NaN</td>
      <td>1.0</td>
      <td>1.000000</td>
      <td>1.0</td>
      <td>14</td>
      <td>0.0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>14</th>
      <th>NaN</th>
      <th>?</th>
      <th>70</th>
      <th>?</th>
      <th></th>
      <th>0</th>
      <th></th>
      <th>0</th>
      <th>?</th>
      <th></th>
      <th>NaN</th>
      <th>NaN</th>
      <td>0.0</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>3</td>
      <td>punct</td>
      <td>NaN</td>
      <td>8</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>PUNCT</td>
      <td></td>
      <td>.</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>3</td>
      <td>NaN</td>
      <td>1</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
<p>1241 rows × 35 columns</p>
</div>


