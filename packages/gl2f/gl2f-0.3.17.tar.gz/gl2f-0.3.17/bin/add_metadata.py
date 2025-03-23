from gl2f.core.local import meta, content

def main():
	archive = meta.load()
	for i in content.get_ids():
		if not i in archive:
			print(f'add metadata for {i}')
			c = content.load(i)
			archive[i] = meta.create(
				important = 'closingAt' in c
			)

	meta.dump_archive(archive)

if __name__ == '__main__':
	main()
