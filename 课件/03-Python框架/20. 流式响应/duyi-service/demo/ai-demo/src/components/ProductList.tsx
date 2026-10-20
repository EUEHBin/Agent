import { useState, useEffect, useCallback } from 'react'
import { Button, Card, Typography, Avatar, Spin } from 'antd'
import { AppstoreOutlined } from '@ant-design/icons'
import { getProducts, type Product } from '../services/api'

const { Text, Paragraph } = Typography
const PAGE_SIZE = 10

interface Props {
  onSelect: (product: Product) => void
  selectedId?: number
}

export default function ProductList({ onSelect, selectedId }: Props) {
  const [products, setProducts] = useState<Product[]>([])
  const [page, setPage] = useState(1)
  const [hasMore, setHasMore] = useState(true)
  const [loading, setLoading] = useState(false)
  const [loadingMore, setLoadingMore] = useState(false)

  const loadProducts = useCallback(async (pageNum: number) => {
    if (pageNum === 1) {
      setLoading(true)
    } else {
      setLoadingMore(true)
    }

    try {
      const res = await getProducts(pageNum, PAGE_SIZE)
      const pageData = res?.data
      const items = pageData?.items || []
      if (pageNum === 1) {
        setProducts(items)
      } else {
        setProducts((prev) => [...prev, ...items])
      }
      const loadedCount = pageNum * PAGE_SIZE
      setHasMore(loadedCount < (pageData?.total || 0))
    } catch (err) {
      console.error('Load products failed:', err)
      if (pageNum === 1) setProducts([])
    } finally {
      setLoading(false)
      setLoadingMore(false)
    }
  }, [])

  useEffect(() => {
    loadProducts(1)
    setPage(1)
  }, [loadProducts])

  const handleLoadMore = () => {
    const nextPage = page + 1
    setPage(nextPage)
    loadProducts(nextPage)
  }

  return (
    <Card
      title="产品列表"
      style={{ height: '100%' }}
      styles={{ body: { padding: 0, height: 'calc(100% - 57px)', overflow: 'auto' } }}
    >
      {loading ? (
        <div style={{ textAlign: 'center', padding: 40 }}>
          <Spin />
        </div>
      ) : (
        <>
          {products.map((item) => (
            <div
              key={item.id}
              onClick={() => onSelect(item)}
              style={{
                padding: '12px 16px',
                cursor: 'pointer',
                background: selectedId === item.id ? '#e6f4ff' : undefined,
                borderBottom: '1px solid #f0f0f0',
                display: 'flex',
                alignItems: 'flex-start',
                gap: 12,
              }}
            >
              <Avatar
                icon={<AppstoreOutlined />}
                style={{ backgroundColor: '#1677ff', flexShrink: 0 }}
              />
              <div style={{ flex: 1, minWidth: 0 }}>
                <Text strong>{item.name}</Text>
                <Paragraph
                  ellipsis={{ rows: 2 }}
                  style={{ marginBottom: 0 }}
                >
                  {item.description}
                </Paragraph>
              </div>
            </div>
          ))}
          {hasMore && (
            <div style={{ textAlign: 'center', padding: '12px 0' }}>
              <Button
                type="link"
                loading={loadingMore}
                onClick={handleLoadMore}
              >
                加载更多
              </Button>
            </div>
          )}
        </>
      )}
    </Card>
  )
}
