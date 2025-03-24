# YinYang Base64

Base64 but Kanji (Yinyang) characters.

Base64 (YinYang) uses the following characters:
```
陰陽天干地支五行金木水火土甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥立春驚蟄清明夏芒種小暑秋白露寒冬大雪雨分穀滿至處霜降生剋沖
```

Base64 (YinYang) padding characters:
```
宮
星宿
```


Base64 (RFC 4648) uses the following characters:
```
ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/
```

Base64 (RFC 4648) padding characters:
```
=
==
```

## Python

Install:
```
pip install yinyang-base64
```

Usage:
```
import yinyang_base64

# Convert bytes to base64 string
utf8_bytes = "Hello World".encode("utf-8")
base64_str = yinyang_base64.get_str(utf8_bytes)
print(base64_str)

# Convert base64 string back to bytes
utf8_bytes = yinyang_base64.get_bytes(base64_str)
print(utf8_bytes)
```


## YinYang (陰陽)

A dualistic concept describing how seemingly opposite forces are interconnected and interdependent.

Yīn/Yam1 (陰): Represents darkness, femininity, cold, passivity, and the moon.

Yáng/Yeung4 (陽): Represents light, masculinity, heat, activity, and the sun.

Everything in the universe contains both Yīn and Yáng, and they constantly interact to maintain balance.

### 天干 (Tin1 Gon1) – The Ten Heavenly Stems

A system of ten characters used in combination with the Earthly Branches to form the Sexagenary Cycle (60-year cycle).

The ten stems are: 甲(Gaap3), 乙(Yut3), 丙(Bing2), 丁(Ding1), 戊(Mou6), 己(Gei2), 庚(Gang1), 辛(San1), 壬(Yam4), 癸(Gwai3).

Each stem is associated with an element from the Five Elements (五行, Ng5 Hang4) and is either Yīn/Yam1(陰) or Yáng/Yeung4(陽).

### 地支 (Dei6 Ji1) – The Twelve Earthly Branches

A system of twelve characters used in the Chinese calendar, astrology, and zodiac system.

The twelve branches correspond to the Chinese zodiac animals:

子(Ji2) – Rat, 丑(Chau2) – Ox, 寅(Yan4) – Tiger, 卯(Maau5) – Rabbit, 辰(San4) – Dragon, 巳(Ji6) – Snake, 午(Ng5) – Horse, 未(Mei6) – Goat, 申(San1) – Monkey, 酉(Yau5) – Rooster, 戌(Seut1) – Dog, 亥(Hoi6) – Pig.

Each branch is also linked to an element from the Five Elements and has a Yīn or Yáng attribute.

### 五行 (Ng5 Hang4) – The Five Elements

A system that describes interactions between elements in nature, used in feng shui, traditional Chinese medicine, astrology, and martial arts.

The five elements are:

Metal (金, Gam1) – Strength, structure

Wood (木, Muk6) – Growth, vitality

Water (水, Seui2) – Flexibility, wisdom

Fire (火, Fo2) – Energy, transformation

Earth (土, Tou2) – Stability, nourishment


The elements interact in two main cycles:

Generating (生, Sang1) cycle: Wood => Fire => Earth => Metal => Water => Wood.

Overcoming (剋, Hak1) cycle: Wood <= Earth <= Water <= Fire <= Metal <= Wood.
