import type { Collection } from '../../types'

interface PromptFiltersProps {
  collections: Collection[]
  activeCollectionId: string
  onCollectionChange: (collectionId: string) => void
}

export function PromptFilters({
  collections,
  activeCollectionId,
  onCollectionChange,
}: PromptFiltersProps) {
  return (
    <label className="field filter-field">
      <span>Filter by Collection</span>
      <select
        value={activeCollectionId}
        onChange={(event) => onCollectionChange(event.target.value)}
      >
        <option value="">All collections</option>
        {collections.map((collection) => (
          <option key={collection.id} value={collection.id}>
            {collection.name}
          </option>
        ))}
      </select>
    </label>
  )
}
