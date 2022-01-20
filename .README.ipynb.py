#!/usr/bin/env python
# coding: utf-8

# # Cadence
# 
# A rhythm analysis toolkit, gathering multiple parsing engines:
# * [Prosodic](https://github.com/quadrismegistus/prosodic) for fast English and Finnish metrical scansion.
# * Cadence itself for slower but exhaustive, MaxEnt-able metrical scansion.

# ## Quickstart

# ### Install
# 
# #### 1. Install python package
# ```
# # install from pypi
# pip install -U cadences    # "cadence" was taken :-/
# 
# # or from github very latest
# pip install -U git+https://github.com/quadrismegistus/cadence
# ```
# 
# #### 2. Insteall espeak (TTS)
# 
# Install espeak, free TTS software, to 'sound out' unknown words. See [here](http://espeak.sourceforge.net/download.html) for all downloads. For Mac or Linux, you can use:
# ```
# apt-get install espeak     # linux
# brew install espeak        # mac
# ```
# If you're on mac and don't have brew installed, do so [here](https://brew.sh/).

# In[3]:


# this should work following installation
import cadence as cd


# ### Load texts

# In[1]:


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


# In[4]:


# These are identical
sonnet = cd.Verse(sonnetXIV)
sonnet = cd.Text(sonnetXIV, linebreaks=True, phrasebreaks=False)


# In[5]:


# Tokenize
sonnet.words()


# In[6]:


# Syllabify
sonnet.sylls()


# In[7]:


# Syntax-parse
sonnet.syntax()


# In[8]:


# Show sentences
sentence = sonnet.sent(1)
sentence.mtree()


# In[9]:


# Stress grid of sentence inferred from syntactic tree
# using metricaltree
sentence.grid()


# ### Parse text

# In[10]:


# Parse lines (verse)
sonnet.parse(num_proc=1,force=True,verbose=True)


# ## Prose

# In[11]:


stop
melville="""Is it that by its indefiniteness it shadows forth the heartless voids and immensities of the universe, and thus stabs us from behind with the thought of annihilation, when beholding the white depths of the milky way? Or is it, that as in essence whiteness is not so much a colour as the visible absence of colour; and at the same time the concrete of all colours; is it for these reasons that there is such a dumb blankness, full of meaning, in a wide landscape of snows: a colourless, all-colour of atheism from which we shrink?"""


# In[ ]:


# So are these
para = cd.Text(melville, prose=True)
para = cd.Text(melville, linebreaks=False, phrasebreaks=True)
para = cd.Prose(melville)

