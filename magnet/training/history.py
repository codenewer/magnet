class History(dict):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.buffer_size = -1
		self.val_buffer_size = -1

	def find(self, key):
		return {k: self[k] for k in self.keys() if key in k}

	def append(self, key, value, validation=False, buffer=False, **stamps):
		if validation: key = 'val_' + key
		buffer_size = self.val_buffer_size if validation else self.buffer_size

		try:
			self[key].append(value, buffer, **stamps)
		except KeyError:
			self[key] = SnapShot(buffer_size)
			self[key].append(value, buffer, **stamps)
		return

	def show(self, key=None, log=False, x_key=None, xlabel=None):
		from matplotlib import pyplot as plt
		if key is None:
			for k in self.keys(): self.show(k, log)
			return

		fig, ax = plt.subplots()
		self[key].show(ax, x_key, label='training')
		try:
			self['val_' + key].show(ax, x_key, label='validation')
		except KeyError: pass

		if log: plt.yscale('log')

		plt.ylabel(key.title())
		if isinstance(xlabel, str):
			plt.xlabel(xlabel)
			plt.title(f'{key.title()} vs {xlabel.title()}')
		elif isinstance(x_key, str):
			plt.xlabel(x_key)
			plt.title(f'{key.title()} vs {x_key.title()}')
		else: plt.title(key.title())
		plt.show()

	def flush(self, key=None, **stamps):
		if key is None:
			for k in self.keys(): self.flush(k, **stamps)
			return

		self[key].flush(**stamps)

class SnapShot:
	def __init__(self, buffer_size=-1):
		self._snaps = []
		if buffer_size is not None:
			self._buffer_size = buffer_size
			self._buffer = SnapShot(buffer_size=None)

	def append(self, value, buffer=False, **stamps):
		if buffer:
			self._buffer.append(value, **stamps)
			if self._buffer_size > 0 and len(self._buffer) > self._buffer_size: self._buffer._pop(0)
			return

		self._snaps.append(dict(val=value, **stamps))

	def flush(self, **stamps):
		if not hasattr(self, '_buffer') or len(self._buffer) == 0: return

		values = self._buffer._retrieve()
		value = sum(values) / len(values)

		self.append(value, **stamps)

		if self._buffer_size < 0: self._buffer._clear()

	def _retrieve(self, key='val'):
		return [snap[key] for snap in self._snaps]

	def _pop(self, index):
		self._snaps.pop(index)

	def _clear(self):
		self._snaps = []

	def __len__(self):
		return len(self._snaps)

	def __getitem__(self, index):
		return self._snaps[index]['val']

	def show(self, ax, x=None, label=None):
		if x is None: x = list(range(len(self)))
		else: x = self._retrieve(x)

		y = self._retrieve()

		if len(x) != len(y): print('Lengths are not the same! Got', len(x), 'and', len(y))

		ax.plot(x, y, label=label)


