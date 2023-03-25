S=spacer
P=cat_ipynb.py
E=python3


self-made: $S.ipynb $P
	$E $P $S.ipynb > $S.py

